from datetime import datetime
from enum import Enum

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.orm import relationship

from app.db.database import Base


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)  # Business contact email
    industry = Column(String, nullable=True)  # Industry type for templates
    api_key = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Original relationships
    knowledge_items = relationship("KnowledgeItem", back_populates="business", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="business", cascade="all, delete-orphan")
    settings = relationship("BusinessSettings", uselist=False)
    
    # New SME relationships
    leads = relationship("Lead", cascade="all, delete-orphan")
    branding = relationship("BusinessBranding", uselist=False, cascade="all, delete-orphan")
    analytics = relationship("ConversationAnalytics", cascade="all, delete-orphan")
    crm_integrations = relationship("CRMIntegration", cascade="all, delete-orphan")
    business_hours = relationship("BusinessHours", uselist=False, cascade="all, delete-orphan")
    product_catalog = relationship("ProductCatalog", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", cascade="all, delete-orphan")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    business = relationship("Business", back_populates="conversations")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    business = relationship("Business", back_populates="knowledge_items")
class BusinessSettings(Base):
    __tablename__ = "business_settings"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), unique=True, nullable=False)

    assistant_name = Column(String, nullable=False, default="Asistente virtual")
    tone = Column(String, nullable=False, default="professional")
    welcome_message = Column(Text, nullable=False, default="Hola, ¿en qué puedo ayudarte?")
    fallback_message = Column(
        Text,
        nullable=False,
        default="Lo siento, no dispongo de esa información en este momento."
    )
    system_prompt = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


# SME Business Enhancement Models

class Lead(Base):
    """Lead generation and customer capture"""
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    
    # Lead Information
    name = Column(String, nullable=True)
    email = Column(String, nullable=True, index=True)
    phone = Column(String, nullable=True)
    company = Column(String, nullable=True)
    
    # Lead Context
    lead_source = Column(String, nullable=False, default="chat_widget")  # chat_widget, api, form
    lead_type = Column(String, nullable=False, default="inquiry")  # inquiry, quote, demo, support
    lead_score = Column(Integer, nullable=False, default=0)  # 0-100 scoring system
    status = Column(String, nullable=False, default="new")  # new, contacted, qualified, converted, closed
    
    # Business Context
    interested_in = Column(Text, nullable=True)  # What they're interested in
    budget_range = Column(String, nullable=True)  # Budget information if provided
    timeline = Column(String, nullable=True)  # When they need the service/product
    notes = Column(Text, nullable=True)  # Additional notes from conversation
    
    # Tracking
    conversion_value = Column(Float, nullable=True)  # Value if converted to sale
    converted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    business = relationship("Business")
    conversation = relationship("Conversation")


class BusinessTemplate(Base):
    """Industry-specific configurations and templates"""
    __tablename__ = "business_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)  # restaurant, retail, services, healthcare, etc.
    display_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Template Configuration
    quick_actions = Column(JSON, nullable=True)  # Predefined quick action buttons
    greeting_template = Column(Text, nullable=False)
    system_prompt_template = Column(Text, nullable=False)
    fallback_messages = Column(JSON, nullable=True)  # Industry-specific fallbacks
    
    # Industry-specific features
    features = Column(JSON, nullable=True)  # Available features for this industry
    integrations = Column(JSON, nullable=True)  # Recommended integrations
    sample_knowledge = Column(JSON, nullable=True)  # Sample FAQ/knowledge items
    
    # Styling
    default_colors = Column(JSON, nullable=True)  # Default color scheme
    icon = Column(String, nullable=True)  # Template icon
    
    created_at = Column(DateTime, default=datetime.utcnow)


class BusinessBranding(Base):
    """Custom branding and styling for businesses"""
    __tablename__ = "business_branding"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), unique=True, nullable=False)
    
    # Visual Branding
    primary_color = Column(String, nullable=False, default="#007bff")
    secondary_color = Column(String, nullable=False, default="#6c757d")
    accent_color = Column(String, nullable=False, default="#28a745")
    text_color = Column(String, nullable=False, default="#333333")
    background_color = Column(String, nullable=False, default="#ffffff")
    
    # Logo and Assets
    logo_url = Column(String, nullable=True)
    favicon_url = Column(String, nullable=True)
    background_image_url = Column(String, nullable=True)
    
    # Typography
    font_family = Column(String, nullable=False, default="system-ui")
    font_size = Column(String, nullable=False, default="14px")
    
    # Widget Customization
    widget_position = Column(String, nullable=False, default="bottom-right")  # bottom-right, bottom-left, etc.
    widget_shape = Column(String, nullable=False, default="circle")  # circle, square, rounded
    avatar_url = Column(String, nullable=True)  # Custom avatar for the assistant
    
    # Messaging
    business_name = Column(String, nullable=True)
    assistant_name = Column(String, nullable=False, default="ChatGenie")
    custom_greeting = Column(Text, nullable=True)
    
    # Advanced Styling
    custom_css = Column(Text, nullable=True)  # Custom CSS overrides
    dark_mode_enabled = Column(Boolean, nullable=False, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    business = relationship("Business")


class ConversationAnalytics(Base):
    """Analytics and metrics for conversations"""
    __tablename__ = "conversation_analytics"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    
    # Time Period
    date = Column(DateTime, nullable=False, index=True)  # Date of metrics (daily aggregation)
    
    # Conversation Metrics
    total_conversations = Column(Integer, nullable=False, default=0)
    total_messages = Column(Integer, nullable=False, default=0)
    avg_conversation_length = Column(Float, nullable=False, default=0.0)  # Average messages per conversation
    avg_response_time = Column(Float, nullable=False, default=0.0)  # Average response time in seconds
    
    # Lead Metrics
    leads_generated = Column(Integer, nullable=False, default=0)
    leads_converted = Column(Integer, nullable=False, default=0)
    conversion_value = Column(Float, nullable=False, default=0.0)
    
    # User Engagement
    unique_visitors = Column(Integer, nullable=False, default=0)
    returning_visitors = Column(Integer, nullable=False, default=0)
    bounce_rate = Column(Float, nullable=False, default=0.0)  # Percentage who left without engaging
    
    # Satisfaction & Quality
    satisfaction_score = Column(Float, nullable=True)  # Average satisfaction rating
    satisfaction_responses = Column(Integer, nullable=False, default=0)
    resolution_rate = Column(Float, nullable=False, default=0.0)  # Percentage of resolved inquiries
    
    # Popular Content
    top_questions = Column(JSON, nullable=True)  # Most frequently asked questions
    popular_actions = Column(JSON, nullable=True)  # Most used quick actions
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    business = relationship("Business")


class CRMIntegration(Base):
    """CRM and webhook integrations"""
    __tablename__ = "crm_integrations"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    
    # Integration Details
    provider = Column(String, nullable=False)  # hubspot, salesforce, pipedrive, zapier, webhook
    integration_name = Column(String, nullable=False)  # Custom name for this integration
    
    # Configuration
    webhook_url = Column(String, nullable=True)  # Webhook endpoint
    api_key = Column(String, nullable=True)  # API key for the integration
    api_secret = Column(String, nullable=True)  # API secret if required
    config = Column(JSON, nullable=True)  # Additional configuration options
    
    # Trigger Settings
    trigger_events = Column(JSON, nullable=False)  # Events that trigger the integration
    lead_mapping = Column(JSON, nullable=True)  # Field mapping configuration
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    last_sync = Column(DateTime, nullable=True)
    sync_status = Column(String, nullable=False, default="pending")  # pending, success, error
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    business = relationship("Business")


class BusinessHours(Base):
    """Business operating hours and timezone management"""
    __tablename__ = "business_hours"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), unique=True, nullable=False)
    
    # Timezone
    timezone = Column(String, nullable=False, default="UTC")
    
    # Operating Hours (24-hour format, e.g., "09:00")
    monday_open = Column(String, nullable=True)
    monday_close = Column(String, nullable=True)
    tuesday_open = Column(String, nullable=True)
    tuesday_close = Column(String, nullable=True)
    wednesday_open = Column(String, nullable=True)
    wednesday_close = Column(String, nullable=True)
    thursday_open = Column(String, nullable=True)
    thursday_close = Column(String, nullable=True)
    friday_open = Column(String, nullable=True)
    friday_close = Column(String, nullable=True)
    saturday_open = Column(String, nullable=True)
    saturday_close = Column(String, nullable=True)
    sunday_open = Column(String, nullable=True)
    sunday_close = Column(String, nullable=True)
    
    # Special handling
    closed_message = Column(Text, nullable=False, default="Estamos cerrados en este momento. Nuestro horario de atención es de lunes a viernes de 9:00 a 18:00.")
    holiday_message = Column(Text, nullable=True)
    after_hours_routing = Column(String, nullable=False, default="message")  # message, email, phone, disabled
    
    # Contact Information
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    website = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    business = relationship("Business")


class ProductCatalog(Base):
    """Product catalog for e-commerce integration"""
    __tablename__ = "product_catalog"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    
    # Product Information
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True, index=True)
    sku = Column(String, nullable=True, index=True)
    
    # Pricing
    price = Column(Float, nullable=True)
    sale_price = Column(Float, nullable=True)
    currency = Column(String, nullable=False, default="USD")
    
    # Inventory
    stock_quantity = Column(Integer, nullable=True)
    in_stock = Column(Boolean, nullable=False, default=True)
    stock_status = Column(String, nullable=False, default="in_stock")  # in_stock, out_of_stock, back_order
    
    # Media
    image_url = Column(String, nullable=True)
    gallery_urls = Column(JSON, nullable=True)  # Additional product images
    
    # E-commerce Integration
    external_id = Column(String, nullable=True, index=True)  # ID in external system (Shopify, WooCommerce)
    external_url = Column(String, nullable=True)  # Link to product page
    
    # Searchability
    search_keywords = Column(Text, nullable=True)  # Keywords for search functionality
    is_featured = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    business = relationship("Business")


class ChatSession(Base):
    """Enhanced chat sessions with visitor tracking"""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    
    # Session Information
    session_id = Column(String, nullable=False, unique=True, index=True)  # UUID for tracking
    visitor_id = Column(String, nullable=True, index=True)  # Anonymous visitor tracking
    
    # Visitor Context
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    country = Column(String, nullable=True)
    referrer = Column(String, nullable=True)
    landing_page = Column(String, nullable=True)
    
    # Session Metrics
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    message_count = Column(Integer, nullable=False, default=0)
    
    # Engagement
    generated_lead = Column(Boolean, nullable=False, default=False)
    satisfaction_rating = Column(Integer, nullable=True)  # 1-5 rating
    was_resolved = Column(Boolean, nullable=True)
    
    # Attribution
    utm_source = Column(String, nullable=True)
    utm_medium = Column(String, nullable=True)
    utm_campaign = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    business = relationship("Business")
    conversation = relationship("Conversation")