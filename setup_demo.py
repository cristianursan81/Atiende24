#!/usr/bin/env python3
"""
Business setup script for Atiende24 demo
Creates a demo business and API key for testing the widget
"""
import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.db.database import get_db, engine
from app.db.models import Base, Business, BusinessSettings
from sqlalchemy.orm import Session
import hashlib
import secrets

def setup_demo_business():
    """Create a demo business for testing"""
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = next(get_db())
    
    try:
        # Check if demo business exists
        existing_business = db.query(Business).filter(Business.id == 1).first()
        
        if existing_business:
            print("✅ Demo business already exists")
            print(f"   Business ID: {existing_business.id}")
            print(f"   Business Name: {existing_business.name}")
            print(f"   API Key: {existing_business.api_key}")
            return existing_business
        
        # Generate a secure API key
        api_key = f"ak-demo-{secrets.token_urlsafe(32)}"
        
        # Create demo business
        demo_business = Business(
            name="Demo Atiende24 Business",
            email="demo@atiende24.com",
            api_key=api_key
        )
        
        db.add(demo_business)
        db.commit()
        db.refresh(demo_business)
        
        # Create default settings
        default_settings = BusinessSettings(
            business_id=demo_business.id,
            welcome_message="¡Hola! 👋 Soy tu asistente virtual inteligente. Estoy aquí para ayudarte las 24 horas del día.\n\n✨ Puedes escribir o usar comandos de voz\n🎯 Tengo acceso a información actualizada\n💡 ¿En qué puedo ayudarte hoy?",
            ai_model="gpt-4o-mini",
            max_tokens=1000,
            temperature=0.7
        )
        
        db.add(default_settings)
        db.commit()
        
        print("🎉 Demo business created successfully!")
        print(f"   Business ID: {demo_business.id}")
        print(f"   Business Name: {demo_business.name}")
        print(f"   API Key: {api_key}")
        print("\n📝 Update your widget configuration:")
        print(f"   businessId: {demo_business.id}")
        print(f'   apiKey: "{api_key}"')
        
        return demo_business
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating demo business: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Setting up Atiende24 Demo Business...")
    print("=" * 50)
    
    try:
        business = setup_demo_business()
        print("\n✅ Setup completed successfully!")
        print("   You can now test the chat widget.")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        sys.exit(1)