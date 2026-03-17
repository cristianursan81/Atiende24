"""
Product Catalog API Endpoints
Routes for managing business products, services, and catalog items
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.db.database import get_db
from app.db.models import Business, ProductCatalog
from app.schemas.sme import (
    ProductCatalogCreate,
    ProductCatalog as ProductCatalogResponse
)

router = APIRouter(prefix="/api/catalog", tags=["Product Catalog"])

@router.post("/", response_model=ProductCatalogResponse)
async def create_product(
    business_id: int,
    product_data: ProductCatalogCreate,
    db: Session = Depends(get_db)
):
    """Add a new product/service to the catalog"""
    
    # Verify business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    # Create product
    product = ProductCatalog(
        business_id=business_id,
        **product_data.dict()
    )
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return product

@router.get("/business/{business_id}", response_model=List[ProductCatalogResponse])
async def get_business_catalog(
    business_id: int,
    category: Optional[str] = None,
    search: Optional[str] = None,
    in_stock_only: bool = False,
    featured_only: bool = False,
    active_only: bool = True,
    sort_by: str = Query(default="name", regex="^(name|price|created_at|stock_quantity)$"),
    sort_order: str = Query(default="asc", regex="^(asc|desc)$"),
    skip: int = 0,
    limit: int = Query(default=50, le=100),
    db: Session = Depends(get_db)
):
    """Get products for a business with filtering and search"""
    
    query = db.query(ProductCatalog).filter(ProductCatalog.business_id == business_id)
    
    # Apply filters
    if category:
        query = query.filter(ProductCatalog.category == category)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                ProductCatalog.name.ilike(search_term),
                ProductCatalog.description.ilike(search_term),
                ProductCatalog.search_keywords.ilike(search_term)
            )
        )
    
    if in_stock_only:
        query = query.filter(ProductCatalog.in_stock == True)
    
    if featured_only:
        query = query.filter(ProductCatalog.is_featured == True)
    
    if active_only:
        query = query.filter(ProductCatalog.is_active == True)
    
    # Apply sorting
    sort_column = getattr(ProductCatalog, sort_by)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    products = query.offset(skip).limit(limit).all()
    
    return products

@router.get("/{product_id}", response_model=ProductCatalogResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID"""
    
    product = db.query(ProductCatalog).filter(ProductCatalog.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product

@router.put("/{product_id}", response_model=ProductCatalogResponse)
async def update_product(
    product_id: int,
    product_update: ProductCatalogCreate,
    db: Session = Depends(get_db)
):
    """Update a product"""
    
    product = db.query(ProductCatalog).filter(ProductCatalog.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update fields
    for field, value in product_update.dict(exclude_unset=True).items():
        setattr(product, field, value)
    
    product.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(product)
    
    return product

@router.delete("/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product"""
    
    product = db.query(ProductCatalog).filter(ProductCatalog.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    db.delete(product)
    db.commit()
    
    return {"message": "Product deleted successfully"}

@router.get("/business/{business_id}/categories")
async def get_catalog_categories(business_id: int, db: Session = Depends(get_db)):
    """Get all categories used in the business catalog"""
    
    categories = db.query(ProductCatalog.category).filter(
        and_(
            ProductCatalog.business_id == business_id,
            ProductCatalog.category.isnot(None),
            ProductCatalog.is_active == True
        )
    ).distinct().all()
    
    category_list = [cat[0] for cat in categories if cat[0]]
    category_counts = {}
    
    for category in category_list:
        count = db.query(ProductCatalog).filter(
            and_(
                ProductCatalog.business_id == business_id,
                ProductCatalog.category == category,
                ProductCatalog.is_active == True
            )
        ).count()
        category_counts[category] = count
    
    return {
        "categories": [
            {"name": cat, "count": category_counts[cat]}
            for cat in sorted(category_list)
        ],
        "total_categories": len(category_list)
    }

@router.get("/business/{business_id}/featured", response_model=List[ProductCatalogResponse])
async def get_featured_products(
    business_id: int,
    limit: int = Query(default=6, le=20),
    db: Session = Depends(get_db)
):
    """Get featured products for display in chat widget"""
    
    products = db.query(ProductCatalog).filter(
        and_(
            ProductCatalog.business_id == business_id,
            ProductCatalog.is_featured == True,
            ProductCatalog.is_active == True
        )
    ).order_by(desc(ProductCatalog.created_at)).limit(limit).all()
    
    return products

@router.get("/business/{business_id}/search")
async def search_catalog(
    business_id: int,
    q: str = Query(..., description="Search query"),
    max_results: int = Query(default=10, le=50),
    db: Session = Depends(get_db)
):
    """Advanced search in product catalog with relevance scoring"""
    
    search_term = f"%{q}%"
    
    # Search with relevance scoring
    products = db.query(ProductCatalog).filter(
        and_(
            ProductCatalog.business_id == business_id,
            ProductCatalog.is_active == True,
            or_(
                ProductCatalog.name.ilike(search_term),
                ProductCatalog.description.ilike(search_term),
                ProductCatalog.search_keywords.ilike(search_term),
                ProductCatalog.category.ilike(search_term)
            )
        )
    ).limit(max_results).all()
    
    # Calculate relevance scores
    scored_results = []
    for product in products:
        score = calculate_relevance_score(product, q.lower())
        scored_results.append({
            "product": ProductCatalogResponse.from_orm(product),
            "relevance_score": score,
            "match_reason": get_match_reason(product, q.lower())
        })
    
    # Sort by relevance score
    scored_results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return {
        "query": q,
        "total_results": len(scored_results),
        "results": scored_results
    }

@router.post("/{product_id}/toggle-featured")
async def toggle_featured_status(product_id: int, db: Session = Depends(get_db)):
    """Toggle the featured status of a product"""
    
    product = db.query(ProductCatalog).filter(ProductCatalog.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product.is_featured = not product.is_featured
    product.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(product)
    
    return {
        "message": f"Product {'featured' if product.is_featured else 'unfeatured'} successfully",
        "is_featured": product.is_featured
    }

@router.post("/{product_id}/update-stock")
async def update_stock(
    product_id: int,
    stock_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Update stock information for a product"""
    
    product = db.query(ProductCatalog).filter(ProductCatalog.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if "stock_quantity" in stock_data:
        product.stock_quantity = stock_data["stock_quantity"]
        product.in_stock = stock_data["stock_quantity"] > 0
    
    if "stock_status" in stock_data:
        product.stock_status = stock_data["stock_status"]
        if stock_data["stock_status"] == "out_of_stock":
            product.in_stock = False
        elif stock_data["stock_status"] == "in_stock":
            product.in_stock = True
    
    if "in_stock" in stock_data:
        product.in_stock = stock_data["in_stock"]
    
    product.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(product)
    
    return {
        "message": "Stock updated successfully",
        "product": ProductCatalogResponse.from_orm(product)
    }

@router.get("/business/{business_id}/analytics")
async def get_catalog_analytics(business_id: int, db: Session = Depends(get_db)):
    """Get catalog analytics and insights"""
    
    total_products = db.query(ProductCatalog).filter(ProductCatalog.business_id == business_id).count()
    active_products = db.query(ProductCatalog).filter(
        and_(ProductCatalog.business_id == business_id, ProductCatalog.is_active == True)
    ).count()
    featured_products = db.query(ProductCatalog).filter(
        and_(
            ProductCatalog.business_id == business_id, 
            ProductCatalog.is_featured == True,
            ProductCatalog.is_active == True
        )
    ).count()
    out_of_stock = db.query(ProductCatalog).filter(
        and_(
            ProductCatalog.business_id == business_id,
            ProductCatalog.in_stock == False,
            ProductCatalog.is_active == True
        )
    ).count()
    
    # Category breakdown
    categories = db.query(
        ProductCatalog.category,
        func.count(ProductCatalog.id).label('count')
    ).filter(
        and_(
            ProductCatalog.business_id == business_id,
            ProductCatalog.is_active == True
        )
    ).group_by(ProductCatalog.category).all()
    
    # Price analysis
    price_stats = db.query(
        func.min(ProductCatalog.price).label('min_price'),
        func.max(ProductCatalog.price).label('max_price'),
        func.avg(ProductCatalog.price).label('avg_price')
    ).filter(
        and_(
            ProductCatalog.business_id == business_id,
            ProductCatalog.price.isnot(None),
            ProductCatalog.is_active == True
        )
    ).first()
    
    return {
        "overview": {
            "total_products": total_products,
            "active_products": active_products,
            "featured_products": featured_products,
            "out_of_stock": out_of_stock,
            "in_stock": active_products - out_of_stock,
            "stock_ratio": ((active_products - out_of_stock) / active_products * 100) if active_products > 0 else 0
        },
        "categories": [
            {"category": cat[0], "count": cat[1]} 
            for cat in categories if cat[0]
        ],
        "pricing": {
            "min_price": float(price_stats.min_price) if price_stats.min_price else 0,
            "max_price": float(price_stats.max_price) if price_stats.max_price else 0,
            "avg_price": float(price_stats.avg_price) if price_stats.avg_price else 0
        } if price_stats else {"min_price": 0, "max_price": 0, "avg_price": 0},
        "recommendations": generate_catalog_recommendations(
            total_products, active_products, featured_products, out_of_stock
        )
    }

@router.post("/business/{business_id}/bulk-import")
async def bulk_import_products(
    business_id: int,
    products_data: List[ProductCatalogCreate],
    db: Session = Depends(get_db)
):
    """Bulk import multiple products"""
    
    # Verify business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found"
        )
    
    created_products = []
    errors = []
    
    for i, product_data in enumerate(products_data):
        try:
            product = ProductCatalog(
                business_id=business_id,
                **product_data.dict()
            )
            db.add(product)
            created_products.append(product)
        
        except Exception as e:
            errors.append({
                "index": i,
                "product_name": product_data.name,
                "error": str(e)
            })
    
    db.commit()
    
    # Refresh created products
    for product in created_products:
        db.refresh(product)
    
    return {
        "message": f"Bulk import completed",
        "created_count": len(created_products),
        "error_count": len(errors),
        "created_products": [ProductCatalogResponse.from_orm(p) for p in created_products],
        "errors": errors
    }

@router.get("/business/{business_id}/widget-config")
async def get_widget_catalog_config(business_id: int, db: Session = Depends(get_db)):
    """Get catalog configuration for chat widget display"""
    
    # Get featured products for widget display
    featured = db.query(ProductCatalog).filter(
        and_(
            ProductCatalog.business_id == business_id,
            ProductCatalog.is_featured == True,
            ProductCatalog.is_active == True
        )
    ).limit(6).all()
    
    # Get categories for filtering
    categories = db.query(ProductCatalog.category).filter(
        and_(
            ProductCatalog.business_id == business_id,
            ProductCatalog.category.isnot(None),
            ProductCatalog.is_active == True
        )
    ).distinct().limit(10).all()
    
    return {
        "featured_products": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description[:100] + "..." if len(p.description or "") > 100 else p.description,
                "price": p.price,
                "sale_price": p.sale_price,
                "currency": p.currency,
                "image_url": p.image_url,
                "in_stock": p.in_stock,
                "category": p.category
            }
            for p in featured
        ],
        "categories": [cat[0] for cat in categories if cat[0]],
        "has_pricing": any(p.price for p in featured),
        "widget_actions": [
            {"text": "🛍️ View Catalog", "action": "show_catalog", "message": "I'd like to see your products"},
            {"text": "⭐ Featured Items", "action": "show_featured", "message": "Show me your featured products"},
            {"text": "🔍 Search Products", "action": "search_products", "message": "I'm looking for something specific"}
        ]
    }


# Utility functions

def calculate_relevance_score(product: ProductCatalog, query: str) -> int:
    """Calculate relevance score for search results"""
    score = 0
    query = query.lower()
    
    # Name match (highest priority)
    if query in (product.name or "").lower():
        score += 100
        if (product.name or "").lower().startswith(query):
            score += 50  # Boost for prefix match
    
    # Description match
    if query in (product.description or "").lower():
        score += 50
    
    # Category match
    if query in (product.category or "").lower():
        score += 30
    
    # Keywords match
    if product.search_keywords and query in product.search_keywords.lower():
        score += 40
    
    # Boost for featured items
    if product.is_featured:
        score += 20
    
    # Boost for in-stock items
    if product.in_stock:
        score += 10
    
    return score

def get_match_reason(product: ProductCatalog, query: str) -> str:
    """Get the reason why this product matched the search"""
    query = query.lower()
    
    if query in (product.name or "").lower():
        return "name"
    elif query in (product.description or "").lower():
        return "description"
    elif query in (product.category or "").lower():
        return "category"
    elif product.search_keywords and query in product.search_keywords.lower():
        return "keywords"
    else:
        return "general"

def generate_catalog_recommendations(total: int, active: int, featured: int, out_of_stock: int) -> List[Dict[str, Any]]:
    """Generate recommendations for catalog improvement"""
    recommendations = []
    
    if total < 10:
        recommendations.append({
            "type": "catalog_size",
            "priority": "medium",
            "message": "Add more products to provide better customer choice",
            "action": "Add 10-20 products to your catalog"
        })
    
    if featured < 3:
        recommendations.append({
            "type": "featured_products",
            "priority": "high", 
            "message": "Feature your best products to increase visibility",
            "action": "Mark 3-6 products as featured"
        })
    
    if out_of_stock > active * 0.3:  # More than 30% out of stock
        recommendations.append({
            "type": "stock_management",
            "priority": "high",
            "message": "High out-of-stock ratio may impact sales",
            "action": "Update stock status or restock popular items"
        })
    
    if total > 0 and active / total < 0.8:  # Less than 80% active
        recommendations.append({
            "type": "active_products",
            "priority": "medium",
            "message": "Many products are inactive",
            "action": "Review and activate relevant products"
        })
    
    return recommendations