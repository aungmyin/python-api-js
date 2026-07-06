import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base, get_db
from main import app

# ============ TEST DATABASE SETUP ============

# Use in-memory SQLite for tests with StaticPool to keep data persistent
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure foreign keys are enabled
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Create all tables once at module load time
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# ============ FIXTURES ============

@pytest.fixture(autouse=True)
def clear_db():
    """Clear all tables before each test"""
    # Get all table names and clear them
    with engine.begin() as conn:
        # Disable foreign keys temporarily
        conn.execute(text("PRAGMA foreign_keys=OFF"))
        # Delete all rows from all tables
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(text(f"DELETE FROM {table.name}"))
        # Re-enable foreign keys
        conn.execute(text("PRAGMA foreign_keys=ON"))
    yield

@pytest.fixture
def user_data():
    """Sample user data"""
    return {
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }

@pytest.fixture
def registered_user(user_data):
    """Register and return a user"""
    response = client.post("/register", json=user_data)
    return response.json()

@pytest.fixture
def auth_token(user_data):
    """Login and return auth token"""
    client.post("/register", json=user_data)
    response = client.post("/login", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(auth_token):
    """Return Authorization headers with Bearer token"""
    return {"Authorization": f"Bearer {auth_token}"}

# ============ AUTHENTICATION TESTS ============

def test_register_user(user_data):
    """Test user registration"""
    response = client.post("/register", json=user_data)
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]
    assert "id" in response.json()

def test_register_duplicate_email(user_data):
    """Test registering with duplicate email"""
    client.post("/register", json=user_data)
    response = client.post("/register", json=user_data)
    assert response.status_code == 400

def test_login_success(user_data):
    """Test successful login"""
    client.post("/register", json=user_data)
    response = client.post("/login", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(user_data):
    """Test login with wrong password"""
    client.post("/register", json=user_data)
    response = client.post("/login", json={
        "email": user_data["email"],
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_get_current_user(registered_user, auth_headers):
    """Test getting current user"""
    response = client.get("/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == registered_user["id"]
    assert response.json()["email"] == registered_user["email"]

def test_get_current_user_no_token():
    """Test accessing protected endpoint without token"""
    response = client.get("/me")
    assert response.status_code == 401

# ============ PRODUCT TESTS ============

def test_list_products():
    """Test listing products"""
    response = client.get("/products")
    assert response.status_code == 200
    assert "items" in response.json()

def test_create_product():
    """Test creating a product"""
    product_data = {
        "name": "New Product",
        "description": "New Description",
        "price": 49.99,
        "stock": 5
    }
    response = client.post("/products", json=product_data)
    assert response.status_code == 200
    assert response.json()["name"] == product_data["name"]
    assert response.json()["price"] == product_data["price"]

def test_create_product_with_category():
    """Test creating a product with category"""
    # Create category first
    cat_response = client.post("/categories", json={
        "name": "Electronics",
        "description": "Electronic devices"
    })
    category_id = cat_response.json()["id"]

    product_data = {
        "name": "Laptop",
        "price": 999.99,
        "stock": 5,
        "category_id": category_id
    }
    response = client.post("/products", json=product_data)
    assert response.status_code == 200
    assert response.json()["category_id"] == category_id

def test_get_product():
    """Test getting a single product"""
    # Create product
    create_response = client.post("/products", json={
        "name": "Test",
        "price": 99.99,
        "stock": 10
    })
    product_id = create_response.json()["id"]

    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test"

def test_get_product_not_found():
    """Test getting non-existent product"""
    response = client.get("/products/999")
    assert response.status_code == 404

def test_update_product():
    """Test updating a product"""
    # Create product
    create_response = client.post("/products", json={
        "name": "Old Name",
        "price": 99.99,
        "stock": 10
    })
    product_id = create_response.json()["id"]

    response = client.put(f"/products/{product_id}", json={
        "name": "New Name",
        "price": 149.99
    })
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"
    assert response.json()["price"] == 149.99

def test_delete_product():
    """Test deleting a product"""
    # Create product
    create_response = client.post("/products", json={
        "name": "Test",
        "price": 99.99,
        "stock": 10
    })
    product_id = create_response.json()["id"]

    response = client.delete(f"/products/{product_id}")
    assert response.status_code == 204

def test_product_pagination():
    """Test product pagination"""
    # Create multiple products
    for i in range(15):
        client.post("/products", json={
            "name": f"Product {i}",
            "price": 50.0 + i,
            "stock": 10
        })

    # Test first page
    response = client.get("/products?skip=0&limit=10")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 10
    assert response.json()["page"] == 1
    assert response.json()["total"] == 15

def test_product_filtering_by_category():
    """Test filtering products by category"""
    # Create categories
    cat1_response = client.post("/categories", json={"name": "Cat1"})
    cat2_response = client.post("/categories", json={"name": "Cat2"})
    cat1_id = cat1_response.json()["id"]
    cat2_id = cat2_response.json()["id"]

    # Create products in different categories
    client.post("/products", json={
        "name": "P1",
        "price": 10.0,
        "stock": 5,
        "category_id": cat1_id
    })
    client.post("/products", json={
        "name": "P2",
        "price": 20.0,
        "stock": 5,
        "category_id": cat2_id
    })

    # Filter by category 1
    response = client.get(f"/products?category_id={cat1_id}")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["name"] == "P1"

# ============ CART TESTS ============

def test_add_to_cart(auth_headers):
    """Test adding item to cart"""
    # Create product
    prod_response = client.post("/products", json={
        "name": "Test",
        "price": 99.99,
        "stock": 10
    })
    product_id = prod_response.json()["id"]

    response = client.post("/cart/items", headers=auth_headers, json={
        "product_id": product_id,
        "quantity": 2
    })
    assert response.status_code == 200
    assert response.json()["quantity"] == 2
    assert response.json()["product_id"] == product_id

def test_add_to_cart_without_auth():
    """Test adding to cart without authentication"""
    response = client.post("/cart/items", json={
        "product_id": 1,
        "quantity": 1
    })
    assert response.status_code == 401

def test_add_nonexistent_product_to_cart(auth_headers):
    """Test adding non-existent product to cart"""
    response = client.post("/cart/items", headers=auth_headers, json={
        "product_id": 999,
        "quantity": 1
    })
    assert response.status_code == 404

def test_get_cart(auth_headers):
    """Test viewing cart"""
    # Create product
    prod_response = client.post("/products", json={
        "name": "Test",
        "price": 99.99,
        "stock": 10
    })
    product_id = prod_response.json()["id"]

    # Add to cart
    client.post("/cart/items", headers=auth_headers, json={
        "product_id": product_id,
        "quantity": 2
    })

    # Get cart
    response = client.get("/cart", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert response.json()["total_price"] == 199.98  # 2 * 99.99

def test_update_cart_item(auth_headers):
    """Test updating cart item quantity"""
    # Create product
    prod_response = client.post("/products", json={
        "name": "Test",
        "price": 99.99,
        "stock": 10
    })
    product_id = prod_response.json()["id"]

    # Add to cart
    add_response = client.post("/cart/items", headers=auth_headers, json={
        "product_id": product_id,
        "quantity": 2
    })
    item_id = add_response.json()["id"]

    # Update quantity
    response = client.put(f"/cart/items/{item_id}", headers=auth_headers, json={
        "quantity": 5
    })
    assert response.status_code == 200
    assert response.json()["quantity"] == 5

def test_remove_from_cart(auth_headers):
    """Test removing item from cart"""
    # Create product
    prod_response = client.post("/products", json={
        "name": "Test",
        "price": 99.99,
        "stock": 10
    })
    product_id = prod_response.json()["id"]

    # Add to cart
    add_response = client.post("/cart/items", headers=auth_headers, json={
        "product_id": product_id,
        "quantity": 2
    })
    item_id = add_response.json()["id"]

    # Remove from cart
    response = client.delete(f"/cart/items/{item_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify cart is empty
    cart_response = client.get("/cart", headers=auth_headers)
    assert len(cart_response.json()["items"]) == 0

# ============ ORDER TESTS ============

def test_checkout(auth_headers):
    """Test checkout"""
    # Create and add product to cart
    prod_response = client.post("/products", json={
        "name": "Test",
        "price": 99.99,
        "stock": 10
    })
    product_id = prod_response.json()["id"]

    client.post("/cart/items", headers=auth_headers, json={
        "product_id": product_id,
        "quantity": 2
    })

    # Checkout
    response = client.post("/checkout", headers=auth_headers, json={})
    assert response.status_code == 200
    assert response.json()["total_price"] == 199.98
    assert response.json()["status"] == "completed"
    assert len(response.json()["items"]) == 1

def test_checkout_empty_cart(auth_headers):
    """Test checkout with empty cart"""
    response = client.post("/checkout", headers=auth_headers, json={})
    assert response.status_code == 400

def test_cart_cleared_after_checkout(auth_headers):
    """Test that cart is cleared after checkout"""
    # Create product
    prod_response = client.post("/products", json={
        "name": "Test",
        "price": 99.99,
        "stock": 10
    })
    product_id = prod_response.json()["id"]

    # Add and checkout
    client.post("/cart/items", headers=auth_headers, json={
        "product_id": product_id,
        "quantity": 1
    })
    client.post("/checkout", headers=auth_headers, json={})

    # Verify cart is empty
    response = client.get("/cart", headers=auth_headers)
    assert len(response.json()["items"]) == 0
    assert response.json()["total_price"] == 0.0

def test_get_orders(auth_headers):
    """Test viewing order history"""
    # Create and checkout
    prod_response = client.post("/products", json={
        "name": "Test",
        "price": 99.99,
        "stock": 10
    })
    product_id = prod_response.json()["id"]

    client.post("/cart/items", headers=auth_headers, json={
        "product_id": product_id,
        "quantity": 1
    })
    client.post("/checkout", headers=auth_headers, json={})

    # Get orders
    response = client.get("/orders", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert len(response.json()["items"]) == 1

def test_get_order_details(auth_headers):
    """Test viewing specific order"""
    # Create and checkout
    prod_response = client.post("/products", json={
        "name": "Test",
        "price": 99.99,
        "stock": 10
    })
    product_id = prod_response.json()["id"]

    client.post("/cart/items", headers=auth_headers, json={
        "product_id": product_id,
        "quantity": 2
    })
    checkout_response = client.post("/checkout", headers=auth_headers, json={})
    order_id = checkout_response.json()["id"]

    # Get order
    response = client.get(f"/orders/{order_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == order_id
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["price_at_purchase"] == 99.99
