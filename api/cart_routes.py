from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from auth_routes import get_current_user_dependency
import models
import schemas
from typing import Optional, List

router = APIRouter()

# ============ CART SCHEMAS ============

class CartItemResponse(schemas.BaseModel):
    id: int
    product_id: int
    quantity: int
    product: schemas.ProductResponse

    class Config:
        from_attributes = True

class CartResponse(schemas.BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponse]
    total_price: float

    class Config:
        from_attributes = True

class AddToCartRequest(schemas.BaseModel):
    product_id: int
    quantity: int = 1

class UpdateCartItemRequest(schemas.BaseModel):
    quantity: int

# ============ CART ENDPOINTS ============

@router.get("/cart", response_model=CartResponse)
async def get_cart(
    current_user: models.User = Depends(get_current_user_dependency),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get current user's cart with all items"""
    cart = db.query(models.Cart).filter(
        models.Cart.user_id == current_user.id
    ).first()

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    # Calculate total price
    total_price = sum(item.quantity * item.product.price for item in cart.items)

    return {
        "id": cart.id,
        "user_id": cart.user_id,
        "items": cart.items,
        "total_price": total_price
    }

@router.post("/cart/items", response_model=CartItemResponse)
async def add_to_cart(
    add_request: AddToCartRequest,
    current_user: models.User = Depends(get_current_user_dependency),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Add a product to the user's cart"""
    # Verify product exists
    product = db.query(models.Product).filter(
        models.Product.id == add_request.product_id
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get user's cart
    cart = db.query(models.Cart).filter(
        models.Cart.user_id == current_user.id
    ).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    # Check if item already in cart
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart.id,
        models.CartItem.product_id == add_request.product_id
    ).first()

    if cart_item:
        # Update quantity if already in cart
        cart_item.quantity += add_request.quantity
    else:
        # Create new cart item
        cart_item = models.CartItem(
            cart_id=cart.id,
            product_id=add_request.product_id,
            quantity=add_request.quantity
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)
    return cart_item

@router.put("/cart/items/{item_id}", response_model=CartItemResponse)
async def update_cart_item(
    item_id: int,
    update_request: UpdateCartItemRequest,
    current_user: models.User = Depends(get_current_user_dependency),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Update quantity of an item in the cart"""
    # Get the cart item
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.id == item_id
    ).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    # Verify the item belongs to the current user's cart
    cart = db.query(models.Cart).filter(
        models.Cart.id == cart_item.cart_id,
        models.Cart.user_id == current_user.id
    ).first()
    if not cart:
        raise HTTPException(status_code=403, detail="Not authorized to modify this cart")

    # Update quantity
    if update_request.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

    cart_item.quantity = update_request.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item

@router.delete("/cart/items/{item_id}", status_code=204)
async def remove_from_cart(
    item_id: int,
    current_user: models.User = Depends(get_current_user_dependency),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Remove an item from the cart"""
    # Get the cart item
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.id == item_id
    ).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    # Verify the item belongs to the current user's cart
    cart = db.query(models.Cart).filter(
        models.Cart.id == cart_item.cart_id,
        models.Cart.user_id == current_user.id
    ).first()
    if not cart:
        raise HTTPException(status_code=403, detail="Not authorized to modify this cart")

    db.delete(cart_item)
    db.commit()

@router.delete("/cart", status_code=204)
async def clear_cart(
    current_user: models.User = Depends(get_current_user_dependency),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Clear all items from the user's cart"""
    # Get user's cart
    cart = db.query(models.Cart).filter(
        models.Cart.user_id == current_user.id
    ).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    # Delete all items in cart
    db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart.id
    ).delete()
    db.commit()
