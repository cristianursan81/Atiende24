"""
CRM Integration API Endpoints
Routes for managing CRM integrations, webhooks, and lead syncing
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import httpx
from urllib.parse import urlparse

from app.db.database import get_db
from app.db.models import Business, CRMIntegration, Lead
from app.schemas.sme import (
    CRMIntegrationCreate,
    CRMIntegrationUpdate,
    CRMIntegration as CRMIntegrationResponse
)

router = APIRouter(prefix="/api/crm", tags=["CRM Integration"])

@router.post("/", response_model=CRMIntegrationResponse)
async def create_crm_integration(
    business_id: int,
    integration_data: CRMIntegrationCreate,
    db: Session = Depends(get_db)
):
    """Create a new CRM integration for a business"""
    
    # Verify business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    # Validate webhook URL if provided
    if integration_data.webhook_url:
        if not is_valid_url(integration_data.webhook_url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook URL format"
            )
    
    # Create integration
    integration = CRMIntegration(
        business_id=business_id,
        provider=integration_data.provider,
        integration_name=integration_data.integration_name,
        webhook_url=integration_data.webhook_url,
        api_key=integration_data.api_key,
        api_secret=integration_data.api_secret,
        config=integration_data.config or {},
        trigger_events=integration_data.trigger_events,
        lead_mapping=integration_data.lead_mapping,
        is_active=True,
        sync_status="configured"
    )
    
    db.add(integration)
    db.commit()
    db.refresh(integration)
    
    return integration

@router.get("/business/{business_id}", response_model=List[CRMIntegrationResponse])
async def get_business_integrations(business_id: int, db: Session = Depends(get_db)):
    """Get all CRM integrations for a business"""
    
    integrations = db.query(CRMIntegration).filter(
        CRMIntegration.business_id == business_id
    ).all()
    
    return integrations

@router.get("/{integration_id}", response_model=CRMIntegrationResponse)
async def get_integration(integration_id: int, db: Session = Depends(get_db)):
    """Get a specific CRM integration"""
    
    integration = db.query(CRMIntegration).filter(CRMIntegration.id == integration_id).first()
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CRM integration not found"
        )
    
    return integration

@router.put("/{integration_id}", response_model=CRMIntegrationResponse)
async def update_integration(
    integration_id: int,
    integration_update: CRMIntegrationUpdate,
    db: Session = Depends(get_db)
):
    """Update a CRM integration"""
    
    integration = db.query(CRMIntegration).filter(CRMIntegration.id == integration_id).first()
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CRM integration not found"
        )
    
    # Update fields
    update_data = integration_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(integration, field, value)
    
    # Validate webhook URL if updated
    if 'webhook_url' in update_data and integration.webhook_url:
        if not is_valid_url(integration.webhook_url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook URL format"
            )
    
    integration.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(integration)
    
    return integration

@router.delete("/{integration_id}")
async def delete_integration(integration_id: int, db: Session = Depends(get_db)):
    """Delete a CRM integration"""
    
    integration = db.query(CRMIntegration).filter(CRMIntegration.id == integration_id).first()
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CRM integration not found"
        )
    
    db.delete(integration)
    db.commit()
    
    return {"message": "CRM integration deleted successfully"}

@router.post("/{integration_id}/test")
async def test_integration(
    integration_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Test a CRM integration with a sample payload"""
    
    integration = db.query(CRMIntegration).filter(CRMIntegration.id == integration_id).first()
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CRM integration not found"
        )
    
    # Create test payload
    test_payload = create_test_payload(integration)
    
    # Test the integration in background
    background_tasks.add_task(test_crm_connection, integration, test_payload, db)
    
    return {
        "message": "Testing CRM integration",
        "integration_name": integration.integration_name,
        "provider": integration.provider,
        "test_payload": test_payload
    }

@router.post("/webhook/{integration_id}/sync")
async def sync_lead_to_crm(
    integration_id: int,
    lead_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Manually sync a specific lead to CRM"""
    
    integration = db.query(CRMIntegration).filter(CRMIntegration.id == integration_id).first()
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CRM integration not found"
        )
    
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    if lead.business_id != integration.business_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lead does not belong to the same business as the integration"
        )
    
    # Sync lead in background
    background_tasks.add_task(sync_lead_to_crm_system, integration, lead, db)
    
    return {
        "message": "Lead sync initiated",
        "lead_id": lead_id,
        "integration": integration.integration_name
    }

@router.get("/providers")
async def get_supported_providers():
    """Get list of supported CRM providers and their configuration requirements"""
    
    providers = {
        "hubspot": {
            "name": "HubSpot",
            "description": "Popular CRM and marketing automation platform",
            "required_fields": ["api_key"],
            "optional_fields": ["webhook_url"],
            "supported_events": ["lead_created", "lead_updated", "lead_converted"],
            "default_mapping": {
                "name": "firstname",
                "email": "email",
                "phone": "phone",
                "company": "company"
            },
            "setup_instructions": "Get your API key from HubSpot Settings > Integrations > API Key"
        },
        "salesforce": {
            "name": "Salesforce",
            "description": "Enterprise CRM solution",
            "required_fields": ["api_key", "api_secret"],
            "optional_fields": ["config.instance_url", "webhook_url"],
            "supported_events": ["lead_created", "lead_updated", "lead_converted"],
            "default_mapping": {
                "name": "Name",
                "email": "Email",
                "phone": "Phone",
                "company": "Company"
            },
            "setup_instructions": "Create Connected App in Salesforce and get Consumer Key/Secret"
        },
        "pipedrive": {
            "name": "Pipedrive",
            "description": "Sales-focused CRM platform",
            "required_fields": ["api_key"],
            "optional_fields": ["config.company_domain", "webhook_url"],
            "supported_events": ["lead_created", "lead_updated", "lead_converted"],
            "default_mapping": {
                "name": "name",
                "email": "email",
                "phone": "phone",
                "company": "org_name"
            },
            "setup_instructions": "Get API key from Pipedrive Settings > API"
        },
        "zapier": {
            "name": "Zapier",
            "description": "Connect to 3000+ apps via Zapier webhooks",
            "required_fields": ["webhook_url"],
            "optional_fields": ["api_key"],
            "supported_events": ["lead_created", "lead_updated", "lead_converted"],
            "default_mapping": {
                "name": "name",
                "email": "email",
                "phone": "phone",
                "company": "company"
            },
            "setup_instructions": "Create a Zapier webhook trigger and use the URL here"
        },
        "webhook": {
            "name": "Custom Webhook",
            "description": "Send data to any custom webhook endpoint",
            "required_fields": ["webhook_url"],
            "optional_fields": ["config.headers", "config.auth_token"],
            "supported_events": ["lead_created", "lead_updated", "lead_converted"],
            "default_mapping": {
                "name": "name",
                "email": "email", 
                "phone": "phone",
                "company": "company"
            },
            "setup_instructions": "Provide any webhook URL that accepts POST requests"
        }
    }
    
    return {"providers": providers}

@router.get("/events")
async def get_supported_events():
    """Get list of supported trigger events"""
    
    events = {
        "lead_created": {
            "name": "Lead Created",
            "description": "Triggered when a new lead is captured",
            "payload_example": {
                "event": "lead_created",
                "lead": {
                    "id": 123,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+1234567890",
                    "company": "Acme Corp",
                    "lead_source": "chat_widget",
                    "lead_score": 75,
                    "created_at": "2023-12-07T10:00:00Z"
                }
            }
        },
        "lead_updated": {
            "name": "Lead Updated",
            "description": "Triggered when lead information is modified",
            "payload_example": {
                "event": "lead_updated",
                "lead": {
                    "id": 123,
                    "status": "qualified",
                    "lead_score": 85,
                    "updated_at": "2023-12-07T11:30:00Z"
                }
            }
        },
        "lead_converted": {
            "name": "Lead Converted",
            "description": "Triggered when a lead is marked as converted",
            "payload_example": {
                "event": "lead_converted",
                "lead": {
                    "id": 123,
                    "status": "converted",
                    "conversion_value": 1500.0,
                    "converted_at": "2023-12-07T15:45:00Z"
                }
            }
        }
    }
    
    return {"events": events}


# Background tasks and utility functions

async def test_crm_connection(integration: CRMIntegration, test_payload: Dict[str, Any], db: Session):
    """Background task to test CRM connection"""
    try:
        if integration.provider == "webhook" or integration.webhook_url:
            # Test webhook
            async with httpx.AsyncClient(timeout=10) as client:
                headers = {"Content-Type": "application/json"}
                
                # Add authentication if configured
                if integration.config and integration.config.get("auth_token"):
                    headers["Authorization"] = f"Bearer {integration.config['auth_token']}"
                
                response = await client.post(
                    integration.webhook_url,
                    json=test_payload,
                    headers=headers
                )
                
                if response.status_code in [200, 201, 202]:
                    integration.sync_status = "success"
                    integration.last_sync = datetime.utcnow()
                    integration.error_message = None
                else:
                    integration.sync_status = "error"
                    integration.error_message = f"Webhook test failed: {response.status_code} {response.text[:200]}"
        
        else:
            # Test Provider-specific API
            success = await test_provider_api(integration, test_payload)
            if success:
                integration.sync_status = "success"
                integration.last_sync = datetime.utcnow()
                integration.error_message = None
            else:
                integration.sync_status = "error"
                integration.error_message = "Provider API test failed"
    
    except Exception as e:
        integration.sync_status = "error"
        integration.error_message = f"Test failed: {str(e)[:200]}"
    
    db.commit()

async def sync_lead_to_crm_system(integration: CRMIntegration, lead: Lead, db: Session):
    """Background task to sync lead to CRM system"""
    try:
        # Create lead payload based on mapping
        payload = create_lead_payload(integration, lead, "lead_created")
        
        if integration.webhook_url:
            # Send via webhook
            async with httpx.AsyncClient(timeout=30) as client:
                headers = {"Content-Type": "application/json"}
                
                # Add authentication if configured
                if integration.config and integration.config.get("auth_token"):
                    headers["Authorization"] = f"Bearer {integration.config['auth_token']}"
                
                response = await client.post(
                    integration.webhook_url,
                    json=payload,
                    headers=headers
                )
                
                if response.status_code in [200, 201, 202]:
                    integration.sync_status = "success"
                    integration.last_sync = datetime.utcnow()
                    integration.error_message = None
                else:
                    integration.sync_status = "error"
                    integration.error_message = f"Sync failed: {response.status_code}"
        
        else:
            # Send to provider API
            success = await sync_to_provider_api(integration, payload)
            if success:
                integration.sync_status = "success"
                integration.last_sync = datetime.utcnow() 
                integration.error_message = None
            else:
                integration.sync_status = "error"
                integration.error_message = "Provider API sync failed"
    
    except Exception as e:
        integration.sync_status = "error"
        integration.error_message = f"Sync failed: {str(e)[:200]}"
    
    db.commit()

def create_test_payload(integration: CRMIntegration) -> Dict[str, Any]:
    """Create a test payload for integration testing"""
    return {
        "event": "test",
        "integration_id": integration.id,
        "integration_name": integration.integration_name,
        "provider": integration.provider,
        "timestamp": datetime.utcnow().isoformat(),
        "test_data": {
            "name": "Test Lead",
            "email": "test@example.com",
            "phone": "+1234567890",
            "company": "Test Company",
            "lead_score": 75
        }
    }

def create_lead_payload(integration: CRMIntegration, lead: Lead, event_type: str) -> Dict[str, Any]:
    """Create lead payload based on CRM integration mapping"""
    
    # Default lead data
    lead_data = {
        "id": lead.id,
        "name": lead.name,
        "email": lead.email,
        "phone": lead.phone,
        "company": lead.company,
        "lead_source": lead.lead_source,
        "lead_type": lead.lead_type,
        "lead_score": lead.lead_score,
        "status": lead.status,
        "interested_in": lead.interested_in,
        "budget_range": lead.budget_range,
        "timeline": lead.timeline,
        "notes": lead.notes,
        "conversion_value": lead.conversion_value,
        "created_at": lead.created_at.isoformat(),
        "updated_at": lead.updated_at.isoformat()
    }
    
    # Apply field mapping if configured
    if integration.lead_mapping:
        mapped_data = {}
        for source_field, target_field in integration.lead_mapping.items():
            if source_field in lead_data and lead_data[source_field]:
                mapped_data[target_field] = lead_data[source_field]
        
        payload = {
            "event": event_type,
            "integration_id": integration.id,
            "timestamp": datetime.utcnow().isoformat(),
            "lead": mapped_data
        }
    else:
        payload = {
            "event": event_type,
            "integration_id": integration.id,
            "timestamp": datetime.utcnow().isoformat(),
            "lead": lead_data
        }
    
    return payload

async def test_provider_api(integration: CRMIntegration, test_payload: Dict[str, Any]) -> bool:
    """Test provider-specific API endpoints"""
    # This would implement actual API testing for each provider
    # For now, return True as mock implementation
    return True

async def sync_to_provider_api(integration: CRMIntegration, payload: Dict[str, Any]) -> bool:
    """Sync data to provider-specific API"""
    # This would implement actual API syncing for each provider
    # For now, return True as mock implementation
    return True

def is_valid_url(url: str) -> bool:
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False