"""
Business Hours Management API Endpoints
Routes for managing business hours, availability, and after-hours behavior
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, time, timedelta
import pytz
from zoneinfo import ZoneInfo

from app.db.database import get_db
from app.db.models import Business, BusinessHours
from app.schemas.sme import (
    BusinessHoursCreate,
    BusinessHours as BusinessHoursResponse
)

router = APIRouter(prefix="/api/business-hours", tags=["Business Hours"])

@router.post("/", response_model=BusinessHoursResponse)
async def create_business_hours(
    business_id: int,
    hours_data: BusinessHoursCreate,
    db: Session = Depends(get_db)
):
    """Create or update business hours for a business"""
    
    # Verify business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    # Check if business hours already exist
    existing_hours = db.query(BusinessHours).filter(BusinessHours.business_id == business_id).first()
    
    if existing_hours:
        # Update existing hours
        for field, value in hours_data.dict(exclude_unset=True).items():
            setattr(existing_hours, field, value)
        
        existing_hours.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_hours)
        return existing_hours
    
    else:
        # Create new hours
        business_hours = BusinessHours(
            business_id=business_id,
            **hours_data.dict()
        )
        
        db.add(business_hours)
        db.commit()
        db.refresh(business_hours)
        return business_hours

@router.get("/business/{business_id}", response_model=BusinessHoursResponse)
async def get_business_hours(business_id: int, db: Session = Depends(get_db)):
    """Get business hours for a specific business"""
    
    hours = db.query(BusinessHours).filter(BusinessHours.business_id == business_id).first()
    if not hours:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business hours not configured for this business"
        )
    
    return hours

@router.put("/business/{business_id}", response_model=BusinessHoursResponse)
async def update_business_hours(
    business_id: int,
    hours_update: BusinessHoursCreate,
    db: Session = Depends(get_db)
):
    """Update business hours for a business"""
    
    hours = db.query(BusinessHours).filter(BusinessHours.business_id == business_id).first()
    if not hours:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business hours not found. Create them first."
        )
    
    # Update fields
    for field, value in hours_update.dict(exclude_unset=True).items():
        setattr(hours, field, value)
    
    hours.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(hours)
    
    return hours

@router.get("/business/{business_id}/status")
async def get_business_status(business_id: int, db: Session = Depends(get_db)):
    """Get current open/closed status of business"""
    
    hours = db.query(BusinessHours).filter(BusinessHours.business_id == business_id).first()
    if not hours:
        return {
            "is_open": True,  # Default to open if no hours configured
            "status": "open",
            "message": "Business hours not configured",
            "next_change": None
        }
    
    # Get current time in business timezone
    try:
        tz = ZoneInfo(hours.timezone)
        current_time = datetime.now(tz)
        current_day = current_time.strftime('%A').lower()
        current_time_only = current_time.time()
        
        # Get today's hours
        open_time = getattr(hours, f"{current_day}_open")
        close_time = getattr(hours, f"{current_day}_close")
        
        if not open_time or not close_time:
            # Closed today
            next_open = get_next_opening_time(hours, current_time)
            return {
                "is_open": False,
                "status": "closed",
                "message": hours.closed_message,
                "next_change": next_open.isoformat() if next_open else None,
                "is_holiday": False
            }
        
        # Parse time strings
        open_time_obj = time.fromisoformat(open_time)
        close_time_obj = time.fromisoformat(close_time)
        
        # Check if currently open
        if open_time_obj <= current_time_only <= close_time_obj:
            # Currently open
            next_close = current_time.replace(
                hour=close_time_obj.hour,
                minute=close_time_obj.minute,
                second=0,
                microsecond=0
            )
            
            return {
                "is_open": True,
                "status": "open",
                "message": f"Open until {close_time}",
                "next_change": next_close.isoformat(),
                "closes_at": close_time,
                "is_holiday": False
            }
        
        else:
            # Currently closed
            next_open = get_next_opening_time(hours, current_time)
            return {
                "is_open": False,
                "status": "closed", 
                "message": hours.closed_message,
                "next_change": next_open.isoformat() if next_open else None,
                "is_holiday": False
            }
    
    except Exception as e:
        # Fallback to open if timezone parsing fails
        return {
            "is_open": True,
            "status": "open",
            "message": f"Unable to determine status: {str(e)}",
            "next_change": None,
            "error": str(e)
        }

@router.get("/business/{business_id}/schedule")
async def get_weekly_schedule(business_id: int, db: Session = Depends(get_db)):
    """Get the weekly schedule for a business"""
    
    hours = db.query(BusinessHours).filter(BusinessHours.business_id == business_id).first()
    if not hours:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business hours not configured"
        )
    
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    schedule = []
    
    for day in days:
        open_time = getattr(hours, f"{day}_open")
        close_time = getattr(hours, f"{day}_close")
        
        schedule.append({
            "day": day.capitalize(),
            "day_code": day,
            "open_time": open_time,
            "close_time": close_time,
            "is_open": bool(open_time and close_time),
            "formatted": format_day_hours(open_time, close_time)
        })
    
    return {
        "business_id": business_id,
        "timezone": hours.timezone,
        "schedule": schedule,
        "closed_message": hours.closed_message,
        "holiday_message": hours.holiday_message,
        "after_hours_routing": hours.after_hours_routing,
        "contact_info": {
            "phone": hours.phone,
            "email": hours.email,
            "address": hours.address,
            "website": hours.website
        }
    }

@router.post("/business/{business_id}/holiday")
async def set_holiday_hours(
    business_id: int,
    holiday_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Set special holiday hours or closure"""
    
    hours = db.query(BusinessHours).filter(BusinessHours.business_id == business_id).first()
    if not hours:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business hours not configured"
        )
    
    # Update holiday message
    if "message" in holiday_data:
        hours.holiday_message = holiday_data["message"]
    
    # Store holiday schedule in config if needed
    if not hours.config:
        hours.config = {}
    
    if "holidays" not in hours.config:
        hours.config["holidays"] = []
    
    # Add holiday to config
    holiday_entry = {
        "date": holiday_data.get("date"),
        "name": holiday_data.get("name", "Holiday"),
        "is_closed": holiday_data.get("is_closed", True),
        "special_hours": holiday_data.get("special_hours"),
        "message": holiday_data.get("message", hours.holiday_message)
    }
    
    hours.config["holidays"].append(holiday_entry)
    hours.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Holiday hours updated successfully",
        "holiday": holiday_entry
    }

@router.get("/business/{business_id}/after-hours-options")
async def get_after_hours_options(business_id: int, db: Session = Depends(get_db)):
    """Get after-hours contact options and routing"""
    
    hours = db.query(BusinessHours).filter(BusinessHours.business_id == business_id).first()
    if not hours:
        return {
            "routing": "message",
            "options": [],
            "message": "We're currently closed. Please leave a message and we'll get back to you."
        }
    
    options = []
    
    if hours.after_hours_routing == "email" and hours.email:
        options.append({
            "type": "email",
            "label": "Send us an email",
            "value": hours.email,
            "action": f"mailto:{hours.email}"
        })
    
    if hours.after_hours_routing == "phone" and hours.phone:
        options.append({
            "type": "phone", 
            "label": "Call us",
            "value": hours.phone,
            "action": f"tel:{hours.phone}"
        })
    
    if hours.after_hours_routing == "message":
        options.append({
            "type": "message",
            "label": "Leave a message",
            "value": "contact_form",
            "action": "show_contact_form"
        })
    
    return {
        "routing": hours.after_hours_routing,
        "options": options,
        "message": hours.closed_message,
        "business_info": {
            "phone": hours.phone,
            "email": hours.email,
            "address": hours.address,
            "website": hours.website
        }
    }

@router.get("/timezones")
async def get_supported_timezones():
    """Get list of supported timezones"""
    
    common_timezones = [
        {"id": "UTC", "name": "UTC (Coordinated Universal Time)", "offset": "+00:00"},
        {"id": "America/New_York", "name": "Eastern Time (US)", "offset": "-05:00/-04:00"},
        {"id": "America/Chicago", "name": "Central Time (US)", "offset": "-06:00/-05:00"},
        {"id": "America/Denver", "name": "Mountain Time (US)", "offset": "-07:00/-06:00"},
        {"id": "America/Los_Angeles", "name": "Pacific Time (US)", "offset": "-08:00/-07:00"},
        {"id": "America/Argentina/Buenos_Aires", "name": "Argentina Time", "offset": "-03:00"},
        {"id": "America/Mexico_City", "name": "Central Standard Time (Mexico)", "offset": "-06:00"},
        {"id": "Europe/London", "name": "Greenwich Mean Time", "offset": "+00:00/+01:00"},
        {"id": "Europe/Paris", "name": "Central European Time", "offset": "+01:00/+02:00"},
        {"id": "Europe/Berlin", "name": "Central European Time", "offset": "+01:00/+02:00"},
        {"id": "Asia/Tokyo", "name": "Japan Standard Time", "offset": "+09:00"},
        {"id": "Asia/Shanghai", "name": "China Standard Time", "offset": "+08:00"},
        {"id": "Asia/Kolkata", "name": "India Standard Time", "offset": "+05:30"},
        {"id": "Australia/Sydney", "name": "Australian Eastern Time", "offset": "+10:00/+11:00"},
    ]
    
    return {"timezones": common_timezones}


# Utility functions

def get_next_opening_time(hours: BusinessHours, current_time: datetime) -> Optional[datetime]:
    """Calculate the next opening time for the business"""
    
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    current_day_index = current_time.weekday()
    
    # Check remaining days in the week
    for i in range(7):
        check_day_index = (current_day_index + i) % 7
        day_name = days[check_day_index]
        
        open_time_str = getattr(hours, f"{day_name}_open")
        if not open_time_str:
            continue
        
        open_time_obj = time.fromisoformat(open_time_str)
        
        # Calculate the datetime for this day
        days_ahead = i
        if i == 0 and current_time.time() >= open_time_obj:
            # Today but already passed opening time, check tomorrow
            continue
        
        next_open_date = current_time.date() + timedelta(days=days_ahead)
        next_open_datetime = datetime.combine(next_open_date, open_time_obj)
        next_open_datetime = next_open_datetime.replace(tzinfo=current_time.tzinfo)
        
        return next_open_datetime
    
    return None

def format_day_hours(open_time: Optional[str], close_time: Optional[str]) -> str:
    """Format day hours for display"""
    
    if not open_time or not close_time:
        return "Closed"
    
    try:
        # Parse and format times
        open_obj = time.fromisoformat(open_time)
        close_obj = time.fromisoformat(close_time)
        
        open_formatted = open_obj.strftime("%I:%M %p").lstrip("0")
        close_formatted = close_obj.strftime("%I:%M %p").lstrip("0")
        
        return f"{open_formatted} - {close_formatted}"
    
    except:
        return f"{open_time} - {close_time}"