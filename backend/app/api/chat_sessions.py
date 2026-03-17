"""
Chat Session Tracking API Endpoints
Routes for managing chat sessions, conversation history, and session analytics
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from app.db.database import get_db
from app.db.models import Business, ChatSession, Lead
from app.schemas.sme import (
    ChatSessionCreate,
    ChatSessionUpdate,
    ChatSessionResponse
)

router = APIRouter(prefix="/api/sessions", tags=["Chat Sessions"])

@router.post("/", response_model=ChatSessionResponse)
async def create_session(
    session_data: ChatSessionCreate,
    db: Session = Depends(get_db)
):
    """Create a new chat session"""
    
    # Verify business exists
    business = db.query(Business).filter(Business.id == session_data.business_id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    # Generate session ID if not provided
    if not session_data.session_id:
        session_data.session_id = str(uuid.uuid4())
    
    # Check if session already exists
    existing_session = db.query(ChatSession).filter(
        ChatSession.session_id == session_data.session_id
    ).first()
    
    if existing_session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session ID already exists"
        )
    
    # Create session
    session = ChatSession(
        business_id=session_data.business_id,
        session_id=session_data.session_id,
        user_id=session_data.user_id,
        user_name=session_data.user_name,
        user_email=session_data.user_email,
        user_phone=session_data.user_phone,
        channel=session_data.channel,
        status="active",
        metadata=session_data.metadata
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session

@router.get("/business/{business_id}", response_model=List[ChatSessionResponse])
async def get_business_sessions(
    business_id: int,
    status: Optional[str] = Query(None, regex="^(active|completed|abandoned)$"),
    channel: Optional[str] = None,
    user_email: Optional[str] = None,
    has_lead: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = Query(default=50, le=100),
    db: Session = Depends(get_db)
):
    """Get chat sessions for a business with filtering"""
    
    query = db.query(ChatSession).filter(ChatSession.business_id == business_id)
    
    # Apply filters
    if status:
        query = query.filter(ChatSession.status == status)
    
    if channel:
        query = query.filter(ChatSession.channel == channel)
    
    if user_email:
        query = query.filter(ChatSession.user_email == user_email)
    
    if has_lead is not None:
        if has_lead:
            # Sessions that generated leads
            lead_session_ids = db.query(Lead.conversation_id).filter(
                Lead.business_id == business_id,
                Lead.conversation_id.isnot(None)
            ).distinct().subquery()
            
            query = query.filter(ChatSession.id.in_(lead_session_ids))
        else:
            # Sessions without leads
            lead_session_ids = db.query(Lead.conversation_id).filter(
                Lead.business_id == business_id,
                Lead.conversation_id.isnot(None)
            ).distinct().subquery()
            
            query = query.filter(~ChatSession.id.in_(lead_session_ids))
    
    if start_date:
        query = query.filter(ChatSession.created_at >= start_date)
    
    if end_date:
        query = query.filter(ChatSession.created_at <= end_date)
    
    # Order by most recent first
    sessions = query.order_by(desc(ChatSession.created_at)).offset(skip).limit(limit).all()
    
    return sessions

@router.get("/{session_id}", response_model=ChatSessionResponse)
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get a specific chat session"""
    
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return session

@router.put("/{session_id}", response_model=ChatSessionResponse)
async def update_session(
    session_id: str,
    session_update: ChatSessionUpdate,
    db: Session = Depends(get_db)
):
    """Update a chat session"""
    
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Update fields
    for field, value in session_update.dict(exclude_unset=True).items():
        setattr(session, field, value)
    
    session.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(session)
    
    return session

@router.post("/{session_id}/add-message")
async def add_message_to_session(
    session_id: str,
    message_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Add a message to the session's conversation history"""
    
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Initialize messages array if not exists
    if "messages" not in session.metadata:
        session.metadata["messages"] = []
    
    # Add message with timestamp
    message = {
        "id": str(uuid.uuid4()),
        "type": message_data.get("type", "user"),  # user, bot, system
        "content": message_data.get("content", ""),
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": message_data.get("metadata", {})
    }
    
    session.metadata["messages"].append(message)
    
    # Update conversation stats
    if "stats" not in session.metadata:
        session.metadata["stats"] = {"message_count": 0, "last_activity": None}
    
    session.metadata["stats"]["message_count"] = len(session.metadata["messages"])
    session.metadata["stats"]["last_activity"] = datetime.utcnow().isoformat()
    
    session.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Message added to session",
        "message_id": message["id"],
        "total_messages": len(session.metadata["messages"])
    }

@router.get("/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    message_type: Optional[str] = Query(None, regex="^(user|bot|system)$"),
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db)
):
    """Get conversation messages for a session"""
    
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    messages = session.metadata.get("messages", [])
    
    # Filter by message type if specified
    if message_type:
        messages = [msg for msg in messages if msg.get("type") == message_type]
    
    # Apply pagination
    paginated_messages = messages[skip:skip + limit]
    
    return {
        "session_id": session_id,
        "total_messages": len(messages),
        "returned_messages": len(paginated_messages),
        "messages": paginated_messages
    }

@router.post("/{session_id}/end")
async def end_session(
    session_id: str,
    end_data: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """End a chat session and mark it as completed"""
    
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session.status = "completed"
    
    # Add session summary to metadata
    if "summary" not in session.metadata:
        session.metadata["summary"] = {}
    
    session.metadata["summary"]["ended_at"] = datetime.utcnow().isoformat()
    session.metadata["summary"]["duration_minutes"] = calculate_session_duration(session)
    session.metadata["summary"]["message_count"] = len(session.metadata.get("messages", []))
    
    if end_data:
        session.metadata["summary"]["end_reason"] = end_data.get("reason", "user_ended")
        session.metadata["summary"]["satisfaction_rating"] = end_data.get("satisfaction")
        session.metadata["summary"]["feedback"] = end_data.get("feedback")
    
    session.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(session)
    
    return {
        "message": "Session ended successfully",
        "session_summary": session.metadata["summary"]
    }

@router.get("/{session_id}/analytics")
async def get_session_analytics(session_id: str, db: Session = Depends(get_db)):
    """Get detailed analytics for a specific session"""
    
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    messages = session.metadata.get("messages", [])
    
    # Basic metrics
    total_messages = len(messages)
    user_messages = len([m for m in messages if m.get("type") == "user"])
    bot_messages = len([m for m in messages if m.get("type") == "bot"])
    
    # Timing analysis
    duration = calculate_session_duration(session)
    
    # Response time analysis
    response_times = calculate_response_times(messages)
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # Check if session generated a lead
    generated_lead = db.query(Lead).filter(Lead.conversation_id == session.id).first()
    
    return {
        "session_id": session_id,
        "duration_minutes": duration,
        "total_messages": total_messages,
        "user_messages": user_messages,
        "bot_messages": bot_messages,
        "avg_response_time_seconds": round(avg_response_time, 2),
        "generated_lead": bool(generated_lead),
        "lead_details": {
            "id": generated_lead.id,
            "status": generated_lead.status,
            "score": generated_lead.lead_score
        } if generated_lead else None,
        "session_quality": assess_session_quality(session, messages, generated_lead),
        "engagement_score": calculate_engagement_score(messages, duration)
    }

@router.get("/business/{business_id}/analytics")
async def get_session_analytics_summary(
    business_id: int,
    period: str = Query(default="week", regex="^(day|week|month|quarter)$"),
    db: Session = Depends(get_db)
):
    """Get session analytics summary for a business"""
    
    # Calculate date range
    end_date = datetime.utcnow()
    if period == "day":
        start_date = end_date - timedelta(days=1)
    elif period == "week":
        start_date = end_date - timedelta(weeks=1)
    elif period == "month":
        start_date = end_date - timedelta(days=30)
    else:  # quarter
        start_date = end_date - timedelta(days=90)
    
    sessions = db.query(ChatSession).filter(
        and_(
            ChatSession.business_id == business_id,
            ChatSession.created_at >= start_date
        )
    ).all()
    
    # Calculate metrics
    total_sessions = len(sessions)
    completed_sessions = len([s for s in sessions if s.status == "completed"])
    active_sessions = len([s for s in sessions if s.status == "active"])
    abandoned_sessions = len([s for s in sessions if s.status == "abandoned"])
    
    # Lead conversion analysis
    sessions_with_leads = db.query(ChatSession).join(Lead).filter(
        and_(
            ChatSession.business_id == business_id,
            ChatSession.created_at >= start_date,
            Lead.conversation_id == ChatSession.id
        )
    ).count()
    
    # Channel breakdown
    channel_stats = {}
    for session in sessions:
        channel = session.channel
        if channel not in channel_stats:
            channel_stats[channel] = {"count": 0, "leads": 0}
        channel_stats[channel]["count"] += 1
    
    # Calculate average session duration
    durations = [calculate_session_duration(s) for s in sessions if s.status == "completed"]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    # Message volume analysis
    total_messages = sum(len(s.metadata.get("messages", [])) for s in sessions)
    avg_messages_per_session = total_messages / total_sessions if total_sessions > 0 else 0
    
    return {
        "period": period,
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "session_overview": {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "active_sessions": active_sessions,
            "abandoned_sessions": abandoned_sessions,
            "completion_rate": (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        },
        "engagement": {
            "avg_duration_minutes": round(avg_duration, 2),
            "avg_messages_per_session": round(avg_messages_per_session, 1),
            "total_messages": total_messages
        },
        "conversion": {
            "sessions_with_leads": sessions_with_leads,
            "lead_conversion_rate": (sessions_with_leads / total_sessions * 100) if total_sessions > 0 else 0
        },
        "channels": [
            {
                "channel": channel,
                "sessions": stats["count"],
                "percentage": round(stats["count"] / total_sessions * 100, 1)
            }
            for channel, stats in channel_stats.items()
        ],
        "recent_sessions": [
            {
                "session_id": s.session_id,
                "status": s.status,
                "channel": s.channel,
                "duration": calculate_session_duration(s),
                "messages": len(s.metadata.get("messages", [])),
                "created_at": s.created_at.isoformat()
            }
            for s in sorted(sessions[:10], key=lambda x: x.created_at, reverse=True)
        ]
    }

@router.post("/{session_id}/abandon")
async def mark_session_abandoned(
    session_id: str,
    abandon_reason: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Mark a session as abandoned"""
    
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session.status = "abandoned"
    
    if "summary" not in session.metadata:
        session.metadata["summary"] = {}
    
    session.metadata["summary"]["abandoned_at"] = datetime.utcnow().isoformat()
    session.metadata["summary"]["abandon_reason"] = abandon_reason or "timeout"
    session.metadata["summary"]["duration_minutes"] = calculate_session_duration(session)
    
    session.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Session marked as abandoned"}


# Utility functions

def calculate_session_duration(session: ChatSession) -> float:
    """Calculate session duration in minutes"""
    
    if session.status == "active":
        return (datetime.utcnow() - session.created_at).total_seconds() / 60
    else:
        return (session.updated_at - session.created_at).total_seconds() / 60

def calculate_response_times(messages: List[Dict[str, Any]]) -> List[float]:
    """Calculate response times between user and bot messages"""
    
    response_times = []
    last_user_message = None
    
    for message in messages:
        if message.get("type") == "user":
            last_user_message = datetime.fromisoformat(message["timestamp"])
        elif message.get("type") == "bot" and last_user_message:
            bot_message_time = datetime.fromisoformat(message["timestamp"])
            response_time = (bot_message_time - last_user_message).total_seconds()
            response_times.append(response_time)
            last_user_message = None
    
    return response_times

def assess_session_quality(session: ChatSession, messages: List[Dict[str, Any]], lead: Optional[Lead]) -> str:
    """Assess the quality of a chat session"""
    
    score = 0
    
    # Message volume (good engagement)
    if len(messages) >= 5:
        score += 30
    elif len(messages) >= 3:
        score += 15
    
    # Generated lead
    if lead:
        score += 40
    
    # Session completion
    if session.status == "completed":
        score += 20
    elif session.status == "abandoned":
        score -= 10
    
    # Duration (not too short, not too long)
    duration = calculate_session_duration(session)
    if 2 <= duration <= 30:
        score += 10
    
    if score >= 70:
        return "excellent"
    elif score >= 50:
        return "good"
    elif score >= 30:
        return "average"
    else:
        return "poor"

def calculate_engagement_score(messages: List[Dict[str, Any]], duration: float) -> int:
    """Calculate engagement score (0-100) based on interaction patterns"""
    
    score = 0
    
    # Message count (max 40 points)
    message_count = len(messages)
    if message_count >= 10:
        score += 40
    elif message_count >= 5:
        score += 20
    elif message_count >= 2:
        score += 10
    
    # Duration engagement (max 30 points)
    if 5 <= duration <= 20:  # Sweet spot
        score += 30
    elif 2 <= duration <= 30:  # Acceptable range
        score += 15
    elif duration > 0:  # At least some time
        score += 5
    
    # User initiative (max 30 points) - user asking questions
    user_messages = [m for m in messages if m.get("type") == "user"]
    questions = sum(1 for m in user_messages if "?" in m.get("content", ""))
    if questions >= 3:
        score += 30
    elif questions >= 1:
        score += 15
    
    return min(score, 100)