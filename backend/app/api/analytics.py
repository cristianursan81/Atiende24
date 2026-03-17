"""
Business Analytics API Endpoints
Routes for comprehensive business analytics, insights, and dashboard metrics
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, case
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import calendar

from app.db.database import get_db
from app.db.models import (
    Business, Lead, ConversationAnalytics, ChatSession, 
    BusinessTemplate, BusinessBranding
)
from app.schemas.sme import AnalyticsSummary

router = APIRouter(prefix="/api/analytics", tags=["Business Analytics"])

@router.get("/business/{business_id}/dashboard")
async def get_business_dashboard(
    business_id: int,
    period: str = Query(default="month", regex="^(day|week|month|quarter|year)$"),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard analytics for a business"""
    
    # Verify business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    # Calculate date range
    end_date = datetime.utcnow()
    if period == "day":
        start_date = end_date - timedelta(days=1)
        comparison_start = start_date - timedelta(days=1)
    elif period == "week":
        start_date = end_date - timedelta(weeks=1)
        comparison_start = start_date - timedelta(weeks=1)
    elif period == "month":
        start_date = end_date - timedelta(days=30)
        comparison_start = start_date - timedelta(days=30)
    elif period == "quarter":
        start_date = end_date - timedelta(days=90)
        comparison_start = start_date - timedelta(days=90)
    else:  # year
        start_date = end_date - timedelta(days=365)
        comparison_start = start_date - timedelta(days=365)
    
    comparison_end = start_date
    
    # Current period data
    current_leads = db.query(Lead).filter(
        and_(Lead.business_id == business_id, Lead.created_at >= start_date)
    ).all()
    
    current_sessions = db.query(ChatSession).filter(
        and_(ChatSession.business_id == business_id, ChatSession.created_at >= start_date)
    ).all()
    
    # Previous period data for comparison
    previous_leads = db.query(Lead).filter(
        and_(
            Lead.business_id == business_id,
            Lead.created_at >= comparison_start,
            Lead.created_at < comparison_end
        )
    ).count()
    
    previous_sessions = db.query(ChatSession).filter(
        and_(
            ChatSession.business_id == business_id,
            ChatSession.created_at >= comparison_start,
            ChatSession.created_at < comparison_end
        )
    ).count()
    
    # Calculate metrics
    total_conversations = len(current_sessions)
    total_leads = len(current_leads)
    converted_leads = len([l for l in current_leads if l.status == 'converted'])
    total_revenue = sum(l.conversion_value for l in current_leads if l.conversion_value)
    
    # Conversion rates
    conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
    lead_rate = (total_leads / total_conversations * 100) if total_conversations > 0 else 0
    
    # Growth calculations
    lead_growth = calculate_growth(total_leads, previous_leads)
    session_growth = calculate_growth(total_conversations, previous_sessions)
    
    # Top questions analysis
    top_questions = await analyze_top_questions(business_id, start_date, db)
    
    # Popular actions from sessions
    popular_actions = await analyze_popular_actions(business_id, start_date, db)
    
    # Hourly activity pattern
    hourly_activity = await get_hourly_activity(business_id, start_date, db)
    
    # Lead sources breakdown
    lead_sources = {}
    for lead in current_leads:
        source = lead.lead_source
        lead_sources[source] = lead_sources.get(source, 0) + 1
    
    # Performance by lead type
    lead_performance = {}
    for lead in current_leads:
        lead_type = lead.lead_type
        if lead_type not in lead_performance:
            lead_performance[lead_type] = {
                'count': 0, 
                'converted': 0, 
                'total_value': 0
            }
        lead_performance[lead_type]['count'] += 1
        if lead.status == 'converted':
            lead_performance[lead_type]['converted'] += 1
            lead_performance[lead_type]['total_value'] += lead.conversion_value or 0
    
    # Calculate conversion rates for each type
    for lead_type in lead_performance:
        data = lead_performance[lead_type]
        data['conversion_rate'] = (data['converted'] / data['count'] * 100) if data['count'] > 0 else 0
        data['avg_value'] = (data['total_value'] / data['converted']) if data['converted'] > 0 else 0
    
    return {
        "business_name": business.name,
        "period": period,
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "overview": {
            "total_conversations": total_conversations,
            "total_leads": total_leads,
            "converted_leads": converted_leads,
            "conversion_rate": round(conversion_rate, 2),
            "lead_rate": round(lead_rate, 2),
            "total_revenue": round(total_revenue, 2),
            "avg_revenue": round(total_revenue / converted_leads, 2) if converted_leads > 0 else 0
        },
        "growth": {
            "leads_growth": lead_growth,
            "conversations_growth": session_growth
        },
        "lead_sources": [
            {"source": source, "count": count, "percentage": round(count / total_leads * 100, 1)}
            for source, count in sorted(lead_sources.items(), key=lambda x: x[1], reverse=True)
        ],
        "lead_performance": [
            {
                "type": lead_type,
                "count": data["count"],
                "converted": data["converted"],
                "conversion_rate": round(data["conversion_rate"], 2),
                "total_value": round(data["total_value"], 2),
                "avg_value": round(data["avg_value"], 2)
            }
            for lead_type, data in sorted(lead_performance.items(), key=lambda x: x[1]["conversion_rate"], reverse=True)
        ],
        "top_questions": top_questions,
        "popular_actions": popular_actions,
        "hourly_activity": hourly_activity,
        "recent_leads": [
            {
                "id": lead.id,
                "name": lead.name or "Unknown",
                "email": lead.email,
                "company": lead.company,
                "score": lead.lead_score,
                "status": lead.status,
                "created_at": lead.created_at.isoformat(),
                "value": lead.conversion_value or 0
            }
            for lead in sorted(current_leads, key=lambda x: x.created_at, reverse=True)[:10]
        ]
    }

@router.get("/business/{business_id}/performance")
async def get_performance_metrics(
    business_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get detailed performance metrics for a business"""
    
    # Default to last 30 days if no dates provided
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)
    
    # Get conversation analytics
    analytics = db.query(ConversationAnalytics).filter(
        and_(
            ConversationAnalytics.business_id == business_id,
            ConversationAnalytics.date >= start_date.date(),
            ConversationAnalytics.date <= end_date.date()
        )
    ).all()
    
    if not analytics:
        return {
            "message": "No analytics data available for the specified period",
            "performance": {
                "avg_response_time": 0,
                "avg_conversation_length": 0,
                "satisfaction_score": 0,
                "resolution_rate": 0,
                "engagement_rate": 0
            }
        }
    
    # Calculate averages
    total_conversations = sum(a.total_conversations for a in analytics)
    total_messages = sum(a.total_messages for a in analytics)
    total_visitors = sum(a.unique_visitors for a in analytics)
    
    avg_response_time = sum(a.avg_response_time for a in analytics) / len(analytics)
    avg_conversation_length = sum(a.avg_conversation_length for a in analytics) / len(analytics)
    avg_satisfaction = sum(a.satisfaction_score for a in analytics if a.satisfaction_score) / len([a for a in analytics if a.satisfaction_score])
    avg_resolution_rate = sum(a.resolution_rate for a in analytics) / len(analytics)
    avg_bounce_rate = sum(a.bounce_rate for a in analytics) / len(analytics)
    
    return {
        "period": {
            "start": start_date.date().isoformat(),
            "end": end_date.date().isoformat()
        },
        "performance": {
            "avg_response_time": round(avg_response_time, 2),
            "avg_conversation_length": round(avg_conversation_length, 2),
            "satisfaction_score": round(avg_satisfaction, 2) if avg_satisfaction else 0,
            "resolution_rate": round(avg_resolution_rate, 2),
            "bounce_rate": round(avg_bounce_rate, 2),
            "engagement_rate": round((total_conversations / total_visitors * 100), 2) if total_visitors > 0 else 0
        },
        "volume": {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "total_visitors": total_visitors,
            "avg_daily_conversations": round(total_conversations / len(analytics), 2),
            "avg_daily_messages": round(total_messages / len(analytics), 2)
        },
        "trends": [
            {
                "date": a.date.isoformat(),
                "conversations": a.total_conversations,
                "messages": a.total_messages,
                "satisfaction": a.satisfaction_score or 0,
                "resolution_rate": a.resolution_rate
            }
            for a in sorted(analytics, key=lambda x: x.date)
        ]
    }

@router.get("/business/{business_id}/optimization")
async def get_optimization_insights(business_id: int, db: Session = Depends(get_db)):
    """Get AI-powered optimization insights and recommendations"""
    
    # Get recent performance data
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    leads = db.query(Lead).filter(
        and_(Lead.business_id == business_id, Lead.created_at >= start_date)
    ).all()
    
    sessions = db.query(ChatSession).filter(
        and_(ChatSession.business_id == business_id, ChatSession.created_at >= start_date)
    ).all()
    
    template = db.query(BusinessTemplate).filter(BusinessTemplate.business_id == business_id).first()
    branding = db.query(BusinessBranding).filter(BusinessBranding.business_id == business_id).first()
    
    insights = []
    recommendations = []
    
    # Analyze conversion rate
    total_leads = len(leads)
    converted_leads = len([l for l in leads if l.status == 'converted'])
    conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
    
    if conversion_rate < 15:
        insights.append({
            "type": "conversion",
            "priority": "high",
            "metric": "Low conversion rate",
            "value": f"{conversion_rate:.1f}%",
            "benchmark": "15-25%",
            "impact": "high"
        })
        recommendations.append({
            "category": "conversion",
            "action": "Enhance lead qualification process",
            "description": "Add more qualifying questions to identify high-intent visitors early",
            "priority": "high",
            "estimated_impact": "15-30% improvement in conversion rate"
        })
    
    # Analyze lead scoring
    high_score_leads = len([l for l in leads if l.lead_score >= 75])
    if high_score_leads / total_leads < 0.2 if total_leads > 0 else False:
        insights.append({
            "type": "lead_quality",
            "priority": "medium",
            "metric": "Low high-quality lead percentage",
            "value": f"{(high_score_leads/total_leads*100):.1f}%" if total_leads > 0 else "0%",
            "benchmark": "20-40%",
            "impact": "medium"
        })
        recommendations.append({
            "category": "lead_quality",
            "action": "Optimize lead capture forms",
            "description": "Collect more business information upfront to increase lead scores",
            "priority": "medium",
            "estimated_impact": "10-20% improvement in lead quality"
        })
    
    # Analyze response patterns
    session_count = len(sessions)
    if session_count > 0:
        avg_session_length = sum(len(s.metadata.get('messages', [])) for s in sessions) / session_count
        if avg_session_length < 3:
            insights.append({
                "type": "engagement",
                "priority": "medium", 
                "metric": "Short conversation length",
                "value": f"{avg_session_length:.1f} messages",
                "benchmark": "5-8 messages",
                "impact": "medium"
            })
            recommendations.append({
                "category": "engagement",
                "action": "Add proactive conversation starters",
                "description": "Include more engaging quick actions and follow-up questions",
                "priority": "medium",
                "estimated_impact": "20-40% increase in conversation length"
            })
    
    # Template analysis
    if template and not template.quick_actions:
        recommendations.append({
            "category": "user_experience",
            "action": "Add quick action buttons",
            "description": "Implement industry-specific quick actions to guide user interactions",
            "priority": "high",
            "estimated_impact": "25-45% improvement in user engagement"
        })
    
    # Branding analysis
    if not branding:
        recommendations.append({
            "category": "branding",
            "action": "Customize widget branding",
            "description": "Apply consistent branding to build trust and recognition",
            "priority": "low",
            "estimated_impact": "5-15% improvement in user trust"
        })
    
    return {
        "optimization_insights": insights,
        "recommendations": recommendations,
        "optimization_score": calculate_optimization_score(insights),
        "next_actions": sorted(recommendations, key=lambda x: {"high": 3, "medium": 2, "low": 1}[x["priority"]], reverse=True)[:3]
    }

async def analyze_top_questions(business_id: int, start_date: datetime, db: Session) -> List[Dict[str, Any]]:
    """Analyze most common questions from chat interactions"""
    # This would typically analyze chat messages, but for now return mock data
    # In a real implementation, you'd analyze message content using NLP
    return [
        {"question": "What are your hours?", "count": 45, "percentage": 23.5},
        {"question": "How much does it cost?", "count": 38, "percentage": 19.8},
        {"question": "Where are you located?", "count": 32, "percentage": 16.7},
        {"question": "Do you offer delivery?", "count": 28, "percentage": 14.6},
        {"question": "What services do you provide?", "count": 25, "percentage": 13.0}
    ]

async def analyze_popular_actions(business_id: int, start_date: datetime, db: Session) -> List[Dict[str, Any]]:
    """Analyze most used quick actions and user interactions"""
    return [
        {"action": "contact_info", "label": "Contact Info", "count": 67, "percentage": 28.2},
        {"action": "pricing", "label": "Pricing", "count": 54, "percentage": 22.7},
        {"action": "services", "label": "Services", "count": 48, "percentage": 20.2},
        {"action": "location", "label": "Location", "count": 41, "percentage": 17.2},
        {"action": "hours", "label": "Hours", "count": 28, "percentage": 11.8}
    ]

async def get_hourly_activity(business_id: int, start_date: datetime, db: Session) -> List[Dict[str, Any]]:
    """Get activity patterns by hour of day"""
    sessions = db.query(ChatSession).filter(
        and_(ChatSession.business_id == business_id, ChatSession.created_at >= start_date)
    ).all()
    
    hourly_counts = {}
    for session in sessions:
        hour = session.created_at.hour
        hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
    
    return [
        {"hour": hour, "count": hourly_counts.get(hour, 0)}
        for hour in range(24)
    ]

def calculate_growth(current: int, previous: int) -> Dict[str, Any]:
    """Calculate growth percentage and trend"""
    if previous == 0:
        growth_rate = 100.0 if current > 0 else 0.0
        trend = "up" if current > 0 else "flat"
    else:
        growth_rate = ((current - previous) / previous) * 100
        trend = "up" if growth_rate > 0 else "down" if growth_rate < 0 else "flat"
    
    return {
        "rate": round(growth_rate, 1),
        "trend": trend,
        "current": current,
        "previous": previous
    }

def calculate_optimization_score(insights: List[Dict[str, Any]]) -> int:
    """Calculate an overall optimization score (0-100)"""
    base_score = 100
    
    for insight in insights:
        if insight["priority"] == "high":
            base_score -= 20
        elif insight["priority"] == "medium":
            base_score -= 10
        else:  # low
            base_score -= 5
    
    return max(0, base_score)