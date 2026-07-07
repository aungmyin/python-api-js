from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database import get_db
from auth_routes import get_current_user_dependency
import models
import schemas
from typing import Optional, List
from datetime import datetime

router = APIRouter()

# ============ ORDER SCHEMAS ============

class OrderItemResponse(schemas.BaseModel):
    id: int
    product_id: int
    quantity: int
    price_at_purchase: float
    product: schemas.ProductResponse

    class Config:
        from_attributes = True

class OrderResponse(schemas.BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True

class OrderListResponse(schemas.BaseModel):
    items: List[OrderResponse]
    total: int

class CheckoutRequest(schemas.BaseModel):
    pass  # No request body needed, uses cart contents

# ============ ORDER ENDPOINTS ============

@router.post("/checkout", response_model=OrderResponse)
async def checkout(
    current_user: models.User = Depends(get_current_user_dependency),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Convert cart to order with stock management and transaction safety"""
    try:
        # Get user's cart
        cart = db.query(models.Cart).filter(
            models.Cart.user_id == current_user.id
        ).first()

        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")

        # Verify cart has items
        if not cart.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot checkout with empty cart"
            )

        # ✅ PHASE 1: Validate all items and stock BEFORE any database changes
        cart_total = 0
        order_items_data = []

        for cart_item in cart.items:
            product = db.query(models.Product).filter(
                models.Product.id == cart_item.product_id
            ).first()

            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product {cart_item.product_id} no longer exists"
                )

            # ✅ Check sufficient stock
            if product.stock < cart_item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for {product.name}. "
                           f"Available: {product.stock}, Requested: {cart_item.quantity}"
                )

            item_total = cart_item.quantity * product.price
            cart_total += item_total
            order_items_data.append({
                "product_id": product.id,
                "quantity": cart_item.quantity,
                "price_at_purchase": product.price
            })

        # ✅ PHASE 2: Create order and items in single transaction
        order = models.Order(
            user_id=current_user.id,
            total_price=cart_total,
            status="completed"
        )
        db.add(order)
        db.flush()  # Get the order ID without committing

        # Create all order items and decrement stock
        for item_data in order_items_data:
            # Get product again (ensure we have fresh data for stock decrement)
            product = db.query(models.Product).filter(
                models.Product.id == item_data["product_id"]
            ).first()

            # Create order item
            order_item = models.OrderItem(
                order_id=order.id,
                product_id=item_data["product_id"],
                quantity=item_data["quantity"],
                price_at_purchase=item_data["price_at_purchase"]
            )
            db.add(order_item)

            # ✅ Decrement stock
            product.stock -= item_data["quantity"]

        # Clear cart items
        for item in cart.items:
            db.delete(item)

        # ✅ PHASE 3: Commit everything at once
        db.commit()
        db.refresh(order)

        return order

    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        db.rollback()
        raise

    except SQLAlchemyError as e:
        # Database errors
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during checkout"
        )

    except Exception as e:
        # Unexpected errors
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Checkout failed: {str(e)}"
        )

@router.get("/orders", response_model=OrderListResponse)
async def get_orders(
    current_user: models.User = Depends(get_current_user_dependency),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get all orders for current user"""
    orders = db.query(models.Order).filter(
        models.Order.user_id == current_user.id
    ).order_by(models.Order.created_at.desc()).all()

    return OrderListResponse(
        items=orders,
        total=len(orders)
    )

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: models.User = Depends(get_current_user_dependency),
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get a specific order (user can only see their own)"""
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order
