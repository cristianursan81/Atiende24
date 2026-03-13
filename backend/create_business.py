from app.db.database import SessionLocal
from app.db.models import Business

db = SessionLocal()

business = Business(name="Demo Negocio")
db.add(business)
db.commit()
db.refresh(business)

print("Business creado con ID:", business.id)

db.close()