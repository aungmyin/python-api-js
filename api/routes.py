from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from auth_routes import get_current_admin_dependency

router = APIRouter()

# ============ CATEGORY ENDPOINTS ============

@router.get("/categories", response_model=list[schemas.CategoryResponse])
async def list_categories(db: Session = Depends(get_db)):
    """List all categories"""
    categories = db.query(models.Category).all()
    return categories

@router.post("/categories", response_model=schemas.CategoryResponse)
async def create_category(
    category: schemas.CategoryCreate,
    current_user: models.User = Depends(get_current_admin_dependency),
    db: Session = Depends(get_db)
):
    """Create a new category (admin only)"""
    db_category = models.Category(
        name=category.name,
        description=category.description
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/categories/{category_id}", response_model=schemas.CategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific category"""
    db_category = db.query(models.Category).filter(
        models.Category.id == category_id
    ).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@router.put("/categories/{category_id}", response_model=schemas.CategoryResponse)
async def update_category(
    category_id: int,
    category: schemas.CategoryUpdate,
    current_user: models.User = Depends(get_current_admin_dependency),
    db: Session = Depends(get_db)
):
    """Update a category (admin only)"""
    db_category = db.query(models.Category).filter(
        models.Category.id == category_id
    ).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    if category.name is not None:
        db_category.name = category.name
    if category.description is not None:
        db_category.description = category.description

    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/categories/{category_id}", status_code=204)
async def delete_category(
    category_id: int,
    current_user: models.User = Depends(get_current_admin_dependency),
    db: Session = Depends(get_db)
):
    """Delete a category (admin only)"""
    db_category = db.query(models.Category).filter(
        models.Category.id == category_id
    ).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(db_category)
    db.commit()

# ============ PRODUCT ENDPOINTS ============

@router.get("/products", response_model=schemas.ProductListResponse)
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """List products with pagination and optional filtering by category"""
    query = db.query(models.Product)

    # Filter by category if provided
    if category_id:
        query = query.filter(models.Product.category_id == category_id)

    # Count total
    total = query.count()

    # Apply pagination
    products = query.offset(skip).limit(limit).all()

    page = skip // limit + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if limit > 0 else 1

    return schemas.ProductListResponse(
        items=products,
        total=total,
        page=page,
        page_size=limit,
        total_pages=total_pages
    )

@router.post("/products", response_model=schemas.ProductResponse)
async def create_product(
    product: schemas.ProductCreate,
    current_user: models.User = Depends(get_current_admin_dependency),
    db: Session = Depends(get_db)
):
    """Create a new product (admin only)"""
    # Verify category exists if provided
    if product.category_id:
        category = db.query(models.Category).filter(
            models.Category.id == product.category_id
        ).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    db_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        category_id=product.category_id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/products/{product_id}", response_model=schemas.ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product"""
    db_product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.put("/products/{product_id}", response_model=schemas.ProductResponse)
async def update_product(
    product_id: int,
    product: schemas.ProductUpdate,
    current_user: models.User = Depends(get_current_admin_dependency),
    db: Session = Depends(get_db)
):
    """Update a product (admin only)"""
    db_product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Verify new category exists if provided
    if product.category_id is not None:
        category = db.query(models.Category).filter(
            models.Category.id == product.category_id
        ).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    if product.name is not None:
        db_product.name = product.name
    if product.description is not None:
        db_product.description = product.description
    if product.price is not None:
        db_product.price = product.price
    if product.stock is not None:
        db_product.stock = product.stock
    if product.category_id is not None:
        db_product.category_id = product.category_id

    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/products/{product_id}", status_code=204)
async def delete_product(
    product_id: int,
    current_user: models.User = Depends(get_current_admin_dependency),
    db: Session = Depends(get_db)
):
    """Delete a product (admin only)"""
    db_product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()
