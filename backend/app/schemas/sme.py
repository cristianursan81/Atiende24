"""
SME Business Enhancement Schemas
Pydantic models for lead generation, templates, and business customization
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr


# Lead Management Schemas

class LeadCreate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    lead_type: str = Field(default="inquiry", pattern="^(inquiry|quote|demo|support)$")
    interested_in: Optional[str] = None
    budget_range: Optional[str] = None
    timeline: Optional[str] = None
    notes: Optional[str] = None


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(new|contacted|qualified|converted|closed)$")
    lead_score: Optional[int] = Field(None, ge=0, le=100)
    interested_in: Optional[str] = None
    budget_range: Optional[str] = None
    timeline: Optional[str] = None
    notes: Optional[str] = None
    conversion_value: Optional[float] = None
    converted_at: Optional[datetime] = None


class Lead(BaseModel):
    id: int
    business_id: int
    conversation_id: Optional[int]
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    lead_source: str
    lead_type: str
    lead_score: int
    status: str
    interested_in: Optional[str]
    budget_range: Optional[str]
    timeline: Optional[str]
    notes: Optional[str]
    conversion_value: Optional[float]
    converted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Business Template Schemas

class BusinessTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    quick_actions: Optional[List[Dict[str, str]]] = None
    greeting_template: str
    system_prompt_template: str
    fallback_messages: Optional[List[str]] = None
    features: Optional[List[str]] = None
    integrations: Optional[List[str]] = None
    sample_knowledge: Optional[List[Dict[str, str]]] = None
    default_colors: Optional[Dict[str, str]] = None
    icon: Optional[str] = None


class BusinessTemplate(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str]
    quick_actions: Optional[List[Dict[str, str]]]
    greeting_template: str
    system_prompt_template: str
    fallback_messages: Optional[List[str]]
    features: Optional[List[str]]
    integrations: Optional[List[str]]
    sample_knowledge: Optional[List[Dict[str, str]]]
    default_colors: Optional[Dict[str, str]]
    icon: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Business Branding Schemas

class BusinessBrandingCreate(BaseModel):
    primary_color: str = "#007bff"
    secondary_color: str = "#6c757d"
    accent_color: str = "#28a745"
    text_color: str = "#333333"
    background_color: str = "#ffffff"
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    background_image_url: Optional[str] = None
    font_family: str = "system-ui"
    font_size: str = "14px"
    widget_position: str = Field(default="bottom-right", pattern="^(bottom-right|bottom-left|top-right|top-left)$")
    widget_shape: str = Field(default="circle", pattern="^(circle|square|rounded)$")
    avatar_url: Optional[str] = None
    business_name: Optional[str] = None
    assistant_name: str = "ChatGenie"
    custom_greeting: Optional[str] = None
    custom_css: Optional[str] = None
    dark_mode_enabled: bool = True


class BusinessBrandingUpdate(BusinessBrandingCreate):
    pass


class BusinessBranding(BaseModel):
    id: int
    business_id: int
    primary_color: str
    secondary_color: str
    accent_color: str
    text_color: str
    background_color: str
    logo_url: Optional[str]
    favicon_url: Optional[str]
    background_image_url: Optional[str]
    font_family: str
    font_size: str
    widget_position: str
    widget_shape: str
    avatar_url: Optional[str]
    business_name: Optional[str]
    assistant_name: str
    custom_greeting: Optional[str]
    custom_css: Optional[str]
    dark_mode_enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Analytics Schemas

class ConversationAnalytics(BaseModel):
    id: int
    business_id: int
    date: datetime
    total_conversations: int
    total_messages: int
    avg_conversation_length: float
    avg_response_time: float
    leads_generated: int
    leads_converted: int
    conversion_value: float
    unique_visitors: int
    returning_visitors: int
    bounce_rate: float
    satisfaction_score: Optional[float]
    satisfaction_responses: int
    resolution_rate: float
    top_questions: Optional[List[str]]
    popular_actions: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


class AnalyticsSummary(BaseModel):
    """Summary analytics for dashboard"""
    period: str  # daily, weekly, monthly
    total_conversations: int
    total_leads: int
    conversion_rate: float
    total_revenue: float
    avg_satisfaction: float
    top_questions: List[Dict[str, Any]]
    popular_actions: List[Dict[str, Any]]
    traffic_sources: List[Dict[str, Any]]
    hourly_activity: List[Dict[str, Any]]
    growth_metrics: Dict[str, float]


# CRM Integration Schemas

class CRMIntegrationCreate(BaseModel):
    provider: str = Field(..., pattern="^(hubspot|salesforce|pipedrive|zapier|webhook)$")
    integration_name: str = Field(..., min_length=1, max_length=100)
    webhook_url: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    trigger_events: List[str] = Field(..., min_items=1)
    lead_mapping: Optional[Dict[str, str]] = None


class CRMIntegrationUpdate(BaseModel):
    integration_name: Optional[str] = Field(None, min_length=1, max_length=100)
    webhook_url: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    trigger_events: Optional[List[str]] = Field(None, min_items=1)
    lead_mapping: Optional[Dict[str, str]] = None
    is_active: Optional[bool] = None


class CRMIntegration(BaseModel):
    id: int
    business_id: int
    provider: str
    integration_name: str
    webhook_url: Optional[str]
    trigger_events: List[str]
    lead_mapping: Optional[Dict[str, str]]
    is_active: bool
    last_sync: Optional[datetime]
    sync_status: str
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Business Hours Schemas

class BusinessHoursCreate(BaseModel):
    timezone: str = "UTC"
    monday_open: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    monday_close: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    tuesday_open: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    tuesday_close: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    wednesday_open: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    wednesday_close: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    thursday_open: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    thursday_close: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    friday_open: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    friday_close: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    saturday_open: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    saturday_close: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    sunday_open: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    sunday_close: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    closed_message: str = "Estamos cerrados en este momento. Nuestro horario de atención es de lunes a viernes de 9:00 a 18:00."
    holiday_message: Optional[str] = None
    after_hours_routing: str = Field(default="message", pattern="^(message|email|phone|disabled)$")
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    website: Optional[str] = None


class BusinessHours(BaseModel):
    id: int
    business_id: int
    timezone: str
    monday_open: Optional[str]
    monday_close: Optional[str]
    tuesday_open: Optional[str]
    tuesday_close: Optional[str]
    wednesday_open: Optional[str]
    wednesday_close: Optional[str]
    thursday_open: Optional[str]
    thursday_close: Optional[str]
    friday_open: Optional[str]
    friday_close: Optional[str]
    saturday_open: Optional[str]
    saturday_close: Optional[str]
    sunday_open: Optional[str]
    sunday_close: Optional[str]
    closed_message: str
    holiday_message: Optional[str]
    after_hours_routing: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    website: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Product Catalog Schemas

class ProductCatalogCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    sale_price: Optional[float] = Field(None, ge=0)
    currency: str = "USD"
    stock_quantity: Optional[int] = Field(None, ge=0)
    in_stock: bool = True
    stock_status: str = Field(default="in_stock", pattern="^(in_stock|out_of_stock|back_order)$")
    image_url: Optional[str] = None
    gallery_urls: Optional[List[str]] = None
    external_id: Optional[str] = None
    external_url: Optional[str] = None
    search_keywords: Optional[str] = None
    is_featured: bool = False
    is_active: bool = True


# Chat Session Schemas
class ChatSessionCreate(BaseModel):
    business_id: int
    session_id: str = Field(..., description="Unique identifier for the chat session")
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user_phone: Optional[str] = None
    channel: str = Field(default="website", description="Channel where chat originated")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatSessionUpdate(BaseModel):
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user_phone: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatSessionResponse(BaseModel):
    id: int
    business_id: int
    session_id: str
    user_id: Optional[str]
    user_name: Optional[str]
    user_email: Optional[str]
    user_phone: Optional[str]
    channel: str
    status: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Response Schemas for API Endpoints

class BusinessTemplateResponse(BaseModel):
    """Response model for business templates"""
    id: int
    business_id: int
    template_name: str
    quick_actions: Optional[List[Dict[str, str]]]
    greeting_template: str
    system_prompt_template: str
    fallback_messages: Optional[List[str]]
    features: Optional[List[str]]
    integrations: Optional[List[str]]
    sample_knowledge: Optional[List[Dict[str, str]]]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BusinessBrandingResponse(BaseModel):
    """Response model for business branding"""
    id: int
    business_id: int
    primary_color: str
    secondary_color: str
    accent_color: str
    text_color: str
    background_color: str
    logo_url: Optional[str]
    favicon_url: Optional[str]
    background_image_url: Optional[str]
    font_family: str
    font_size: str
    widget_position: str
    widget_shape: str
    avatar_url: Optional[str]
    business_name: Optional[str]
    assistant_name: str
    custom_greeting: Optional[str]
    custom_css: Optional[str]
    dark_mode_enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    """Response model for template list"""
    name: str = Field(..., description="Template internal name")
    display_name: str = Field(..., description="Human readable template name")
    description: str = Field(..., description="Template description")
    icon: str = Field(..., description="Template icon/emoji")


class ProductCatalogUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    sale_price: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    in_stock: Optional[bool] = None
    stock_status: Optional[str] = Field(None, pattern="^(in_stock|out_of_stock|back_order)$")
    image_url: Optional[str] = None
    gallery_urls: Optional[List[str]] = None
    external_id: Optional[str] = None
    external_url: Optional[str] = None
    search_keywords: Optional[str] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None


class ProductCatalog(BaseModel):
    id: int
    business_id: int
    name: str
    description: Optional[str]
    category: Optional[str]
    sku: Optional[str]
    price: Optional[float]
    sale_price: Optional[float]
    currency: str
    stock_quantity: Optional[int]
    in_stock: bool
    stock_status: str
    image_url: Optional[str]
    gallery_urls: Optional[List[str]]
    external_id: Optional[str]
    external_url: Optional[str]
    search_keywords: Optional[str]
    is_featured: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Chat Widget Configuration Response

class ChatWidgetConfig(BaseModel):
    """Complete widget configuration for frontend"""
    business: Dict[str, Any]
    branding: BusinessBranding
    business_hours: Optional[BusinessHours]
    templates: Dict[str, Any]
    features: Dict[str, bool]
    quick_actions: List[Dict[str, str]]
    
    class Config:
        from_attributes = True