"""
Industry Templates API Endpoints
Routes for managing business industry templates
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.db.database import get_db
from app.db.models import Business, BusinessTemplate, BusinessBranding
from app.schemas.sme import (
    BusinessTemplateCreate,
    BusinessTemplateResponse,
    BusinessBrandingCreate,
    BusinessBrandingResponse,
    TemplateListResponse
)
from app.services.industry_templates import IndustryTemplates

router = APIRouter(prefix="/api/templates", tags=["Industry Templates"])

@router.get("/", response_model=List[TemplateListResponse])
async def get_available_templates():
    """Get all available industry templates"""
    templates = IndustryTemplates.get_template_list()
    return [
        TemplateListResponse(
            name=template["name"],
            display_name=template["display_name"],
            description=template["description"],
            icon=template["icon"]
        )
        for template in templates
    ]

@router.get("/{template_name}", response_model=Dict[str, Any])
async def get_template_details(template_name: str):
    """Get detailed configuration for a specific template"""
    template = IndustryTemplates.get_template(template_name)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{template_name}' not found"
        )
    return template

@router.post("/apply/{business_id}")
async def apply_template_to_business(
    business_id: int,
    template_name: str,
    customizations: Dict[str, Any] = None,
    db: Session = Depends(get_db)
):
    """Apply an industry template to a business"""
    # Get the business
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    # Get the template
    template = IndustryTemplates.get_template(template_name)
    
    # Create or update business template
    db_template = db.query(BusinessTemplate).filter(
        BusinessTemplate.business_id == business_id
    ).first()
    
    if db_template:
        # Update existing template
        db_template.template_name = template_name
        db_template.quick_actions = template["quick_actions"]
        db_template.greeting_template = template["greeting_template"]
        db_template.system_prompt_template = template["system_prompt_template"]
        db_template.fallback_messages = template["fallback_messages"]
        db_template.features = template["features"]
        db_template.integrations = template["integrations"]
        db_template.sample_knowledge = template["sample_knowledge"]
        
        # Apply customizations if provided
        if customizations:
            for key, value in customizations.items():
                if hasattr(db_template, key):
                    setattr(db_template, key, value)
    else:
        # Create new template
        template_data = BusinessTemplateCreate(
            business_id=business_id,
            template_name=template_name,
            quick_actions=template["quick_actions"],
            greeting_template=template["greeting_template"],
            system_prompt_template=template["system_prompt_template"],
            fallback_messages=template["fallback_messages"],
            features=template["features"],
            integrations=template["integrations"],
            sample_knowledge=template["sample_knowledge"]
        )
        
        db_template = BusinessTemplate(**template_data.dict())
        db.add(db_template)
    
    # Create or update business branding
    db_branding = db.query(BusinessBranding).filter(
        BusinessBranding.business_id == business_id
    ).first()
    
    if db_branding:
        # Update existing branding
        db_branding.primary_color = template["default_colors"]["primary"]
        db_branding.secondary_color = template["default_colors"]["secondary"]
        db_branding.accent_color = template["default_colors"]["accent"]
        db_branding.background_color = template["default_colors"]["background"]
        
        # Apply branding customizations
        if customizations and "branding" in customizations:
            for key, value in customizations["branding"].items():
                if hasattr(db_branding, key):
                    setattr(db_branding, key, value)
    else:
        # Create new branding
        branding_data = BusinessBrandingCreate(
            business_id=business_id,
            primary_color=template["default_colors"]["primary"],
            secondary_color=template["default_colors"]["secondary"],
            accent_color=template["default_colors"]["accent"],
            background_color=template["default_colors"]["background"],
            logo_url="",
            font_family="Inter, sans-serif",
            widget_position="bottom-right",
            widget_size="medium",
            custom_css=""
        )
        
        db_branding = BusinessBranding(**branding_data.dict())
        db.add(db_branding)
    
    # Update business industry if not set
    if not business.industry:
        business.industry = template_name
    
    db.commit()
    db.refresh(db_template)
    db.refresh(db_branding)
    
    return {
        "message": f"Template '{template_name}' applied successfully to {business.name}",
        "template": BusinessTemplateResponse.from_orm(db_template),
        "branding": BusinessBrandingResponse.from_orm(db_branding)
    }

@router.get("/business/{business_id}")
async def get_business_template(business_id: int, db: Session = Depends(get_db)):
    """Get the current template configuration for a business"""
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    template = db.query(BusinessTemplate).filter(
        BusinessTemplate.business_id == business_id
    ).first()
    
    branding = db.query(BusinessBranding).filter(
        BusinessBranding.business_id == business_id
    ).first()
    
    if not template:
        return {
            "message": "No template configured for this business",
            "template": None,
            "branding": None,
            "suggested_templates": IndustryTemplates.get_template_list()[:3]
        }
    
    return {
        "template": BusinessTemplateResponse.from_orm(template),
        "branding": BusinessBrandingResponse.from_orm(branding) if branding else None,
        "business": {
            "name": business.name,
            "industry": business.industry,
            "description": business.description
        }
    }

@router.put("/business/{business_id}/customize")
async def customize_business_template(
    business_id: int,
    customizations: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Customize the template configuration for a business"""
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    template = db.query(BusinessTemplate).filter(
        BusinessTemplate.business_id == business_id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No template configured for this business. Apply a template first."
        )
    
    # Apply template customizations
    if "template" in customizations:
        for key, value in customizations["template"].items():
            if hasattr(template, key):
                setattr(template, key, value)
    
    # Apply branding customizations
    if "branding" in customizations:
        branding = db.query(BusinessBranding).filter(
            BusinessBranding.business_id == business_id
        ).first()
        
        if branding:
            for key, value in customizations["branding"].items():
                if hasattr(branding, key):
                    setattr(branding, key, value)
    
    db.commit()
    db.refresh(template)
    
    return {
        "message": "Template customizations applied successfully",
        "template": BusinessTemplateResponse.from_orm(template)
    }

@router.post("/business/{business_id}/reset")
async def reset_business_template(
    business_id: int,
    template_name: str = None,
    db: Session = Depends(get_db)
):
    """Reset business template to default configuration"""
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    # Use current template if none specified
    if not template_name:
        current_template = db.query(BusinessTemplate).filter(
            BusinessTemplate.business_id == business_id
        ).first()
        
        if current_template:
            template_name = current_template.template_name
        else:
            template_name = "general"
    
    # Get fresh template configuration
    template_config = IndustryTemplates.get_template(template_name)
    
    # Remove existing configurations
    db.query(BusinessTemplate).filter(
        BusinessTemplate.business_id == business_id
    ).delete()
    
    db.query(BusinessBranding).filter(
        BusinessBranding.business_id == business_id
    ).delete()
    
    db.commit()
    
    # Apply fresh template
    return await apply_template_to_business(business_id, template_name, None, db)

@router.get("/preview/{template_name}")
async def preview_template_widget(template_name: str):
    """Get widget preview configuration for a template"""
    template = IndustryTemplates.get_template(template_name)
    
    # Generate preview configuration
    preview_config = {
        "colors": template["default_colors"],
        "quick_actions": template["quick_actions"][:4],  # Show only first 4
        "greeting": template["greeting_template"].replace("{business_name}", "Tu Negocio"),
        "icon": template["icon"],
        "sample_messages": [
            {
                "type": "user",
                "text": "¡Hola! ¿Cómo están?"
            },
            {
                "type": "bot", 
                "text": template["greeting_template"].replace("{business_name}", "Tu Negocio")
            }
        ]
    }
    
    return preview_config