"""
Lead Generation API Endpoints
Routes for managing leads, lead scoring, and lead conversion tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.db.database import get_db
from app.db.models import Business, Lead, ConversationAnalytics, ChatSession
from app.schemas.sme import (
    LeadCreate,
    LeadUpdate,
    Lead as LeadResponse
)

router = APIRouter(prefix="/api/leads", tags=["Lead Generation"])

@router.post("/", response_model=LeadResponse)
async def create_lead(
    business_id: int,
    lead_data: LeadCreate,
    conversation_id: Optional[int] = None,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create a new lead from chat interaction"""
    # Verify business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    # Auto-populate lead source if session provided
    lead_source = "chat_widget"
    if session_id:
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if session:
            lead_source = f"{session.channel}_chat"
            conversation_id = session.id
    
    # Calculate initial lead score
    lead_score = calculate_lead_score(lead_data)
    
    # Create lead
    lead = Lead(
        business_id=business_id,
        conversation_id=conversation_id,
        name=lead_data.name,
        email=lead_data.email,
        phone=lead_data.phone,
        company=lead_data.company,
        lead_source=lead_source,
        lead_type=lead_data.lead_type,
        lead_score=lead_score,
        status="new",
        interested_in=lead_data.interested_in,
        budget_range=lead_data.budget_range,
        timeline=lead_data.timeline,
        notes=lead_data.notes
    )
    
    db.add(lead)
    db.commit()
    db.refresh(lead)
    
    return lead

@router.get("/", response_model=List[LeadResponse])
async def get_leads(
    business_id: int,
    status: Optional[str] = Query(None, regex="^(new|contacted|qualified|converted|closed)$"),
    lead_type: Optional[str] = Query(None, regex="^(inquiry|quote|demo|support)$"),
    lead_source: Optional[str] = None,
    min_score: Optional[int] = Query(None, ge=0, le=100),
    max_score: Optional[int] = Query(None, ge=0, le=100),
    skip: int = 0,
    limit: int = Query(default=50, le=100),
    db: Session = Depends(get_db)
):
    """Get leads for a business with filtering options"""
    query = db.query(Lead).filter(Lead.business_id == business_id)
    
    # Apply filters
    if status:
        query = query.filter(Lead.status == status)
    
    if lead_type:
        query = query.filter(Lead.lead_type == lead_type)
    
    if lead_source:
        query = query.filter(Lead.lead_source == lead_source)
    
    if min_score is not None:
        query = query.filter(Lead.lead_score >= min_score)
    
    if max_score is not None:
        query = query.filter(Lead.lead_score <= max_score)
    
    # Order by score (highest first) and creation date
    leads = query.order_by(desc(Lead.lead_score), desc(Lead.created_at)).offset(skip).limit(limit).all()
    
    return leads

@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: int, db: Session = Depends(get_db)):
    """Get a specific lead by ID"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    return lead

@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    lead_update: LeadUpdate,
    db: Session = Depends(get_db)
):
    """Update a lead"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Update fields
    for field, value in lead_update.dict(exclude_unset=True).items():
        setattr(lead, field, value)
    
    # Recalculate lead score if relevant fields changed
    if any(field in lead_update.dict(exclude_unset=True) for field in 
           ['email', 'phone', 'company', 'budget_range', 'timeline']):
        new_score = calculate_lead_score_from_lead(lead)
        lead.lead_score = new_score
    
    db.commit()
    db.refresh(lead)
    
    return lead

@router.delete("/{lead_id}")
async def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    """Delete a lead"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    db.delete(lead)
    db.commit()
    
    return {"message": "Lead deleted successfully"}

@router.get("/business/{business_id}/analytics")
async def get_lead_analytics(
    business_id: int,
    period: str = Query(default="week", regex="^(day|week|month|quarter|year)$"),
    db: Session = Depends(get_db)
):
    """Get lead analytics for a business"""
    # Calculate date range
    end_date = datetime.utcnow()
    if period == "day":
        start_date = end_date - timedelta(days=1)
    elif period == "week":
        start_date = end_date - timedelta(weeks=1)
    elif period == "month":
        start_date = end_date - timedelta(days=30)
    elif period == "quarter":
        start_date = end_date - timedelta(days=90)
    else:  # year
        start_date = end_date - timedelta(days=365)
    
    # Get leads in period
    leads = db.query(Lead).filter(
        and_(
            Lead.business_id == business_id,
            Lead.created_at >= start_date,
            Lead.created_at <= end_date
        )
    ).all()
    
    # Calculate metrics
    total_leads = len(leads)
    qualified_leads = len([l for l in leads if l.status in ['qualified', 'converted']])
    converted_leads = len([l for l in leads if l.status == 'converted'])
    total_value = sum(l.conversion_value for l in leads if l.conversion_value)
    
    # Lead sources breakdown
    sources = {}
    for lead in leads:
        sources[lead.lead_source] = sources.get(lead.lead_source, 0) + 1
    
    # Lead types breakdown
    types = {}
    for lead in leads:
        types[lead.lead_type] = types.get(lead.lead_type, 0) + 1
    
    # Score distribution
    score_ranges = {"0-25": 0, "26-50": 0, "51-75": 0, "76-100": 0}
    for lead in leads:
        score = lead.lead_score
        if score <= 25:
            score_ranges["0-25"] += 1
        elif score <= 50:
            score_ranges["26-50"] += 1
        elif score <= 75:
            score_ranges["51-75"] += 1
        else:
            score_ranges["76-100"] += 1
    
    return {
        "period": period,
        "total_leads": total_leads,
        "qualified_leads": qualified_leads,
        "converted_leads": converted_leads,
        "conversion_rate": (converted_leads / total_leads * 100) if total_leads > 0 else 0,
        "qualification_rate": (qualified_leads / total_leads * 100) if total_leads > 0 else 0,
        "total_value": total_value,
        "average_value": (total_value / converted_leads) if converted_leads > 0 else 0,
        "lead_sources": sources,
        "lead_types": types,
        "score_distribution": score_ranges,
        "top_performers": [
            {
                "id": l.id,
                "name": l.name or "Unknown",
                "score": l.lead_score,
                "status": l.status,
                "value": l.conversion_value or 0
            }
            for l in sorted(leads, key=lambda x: x.lead_score, reverse=True)[:5]
        ]
    }

@router.post("/{lead_id}/convert")
async def convert_lead(
    lead_id: int,
    conversion_value: Optional[float] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Mark a lead as converted"""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    lead.status = "converted"
    lead.converted_at = datetime.utcnow()
    
    if conversion_value is not None:
        lead.conversion_value = conversion_value
    
    if notes:
        lead.notes = f"{lead.notes}\n[CONVERSION] {notes}" if lead.notes else f"[CONVERSION] {notes}"
    
    db.commit()
    db.refresh(lead)
    
    return {
        "message": "Lead converted successfully",
        "lead": lead,
        "conversion_value": lead.conversion_value
    }

@router.get("/business/{business_id}/scoring")
async def get_lead_scoring_info(business_id: int):
    """Get information about lead scoring algorithm"""
    return {
        "scoring_criteria": {
            "contact_completeness": {"max_points": 30, "description": "Having email, phone, and name"},
            "business_info": {"max_points": 20, "description": "Company name provided"},
            "engagement_level": {"max_points": 25, "description": "Based on lead type and interest"},
            "budget_qualification": {"max_points": 15, "description": "Budget range specified"},
            "timeline_urgency": {"max_points": 10, "description": "Timeline urgency"}
        },
        "score_ranges": {
            "hot": {"min": 76, "max": 100, "description": "High-priority leads ready for immediate contact"},
            "warm": {"min": 51, "max": 75, "description": "Qualified leads worth nurturing"},
            "cold": {"min": 26, "max": 50, "description": "Low-priority leads for long-term follow-up"},
            "unqualified": {"min": 0, "max": 25, "description": "Insufficient information or interest"}
        }
    }

def calculate_lead_score(lead_data: LeadCreate) -> int:
    """Calculate lead score based on provided information"""
    score = 0
    
    # Contact completeness (30 points max)
    if lead_data.email:
        score += 15
    if lead_data.phone:
        score += 10
    if lead_data.name:
        score += 5
    
    # Business information (20 points max)
    if lead_data.company:
        score += 20
    
    # Engagement level based on lead type (25 points max)
    engagement_scores = {
        "inquiry": 10,
        "quote": 25,
        "demo": 20,
        "support": 5
    }
    score += engagement_scores.get(lead_data.lead_type, 0)
    
    # Budget qualification (15 points max)
    if lead_data.budget_range:
        # Higher scores for higher budget ranges
        budget_scores = {
            "under_1k": 5,
            "1k_5k": 8,
            "5k_10k": 12,
            "10k_plus": 15,
            "enterprise": 15
        }
        score += budget_scores.get(lead_data.budget_range, 5)
    
    # Timeline urgency (10 points max)
    if lead_data.timeline:
        timeline_scores = {
            "immediate": 10,
            "this_month": 8,
            "next_month": 6,
            "this_quarter": 4,
            "next_quarter": 2,
            "exploring": 1
        }
        score += timeline_scores.get(lead_data.timeline, 0)
    
    return min(score, 100)  # Cap at 100

def calculate_lead_score_from_lead(lead: Lead) -> int:
    """Recalculate lead score from existing lead data"""
    # Create LeadCreate object to reuse scoring logic
    lead_data = LeadCreate(
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        company=lead.company,
        lead_type=lead.lead_type,
        interested_in=lead.interested_in,
        budget_range=lead.budget_range,
        timeline=lead.timeline,
        notes=lead.notes
    )
    return calculate_lead_score(lead_data)