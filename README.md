# Shopping Cart REST API

A full-stack learning project demonstrating a complete REST API with FastAPI, PostgreSQL, and Docker.

**Tech Stack:**
- Backend: Python 3.12, FastAPI, SQLAlchemy, Alembic
- Database: PostgreSQL 16
- Frontend: (Phase 2) Vanilla JavaScript + Vite
- Containerization: Docker & Docker Compose

---

## Quick Start

### Prerequisites

- Docker Desktop (running)
- Git

### Run Everything with One Command

```bash
docker compose up --build
```

This starts:
- **PostgreSQL** on `localhost:5432`
- **FastAPI** on `localhost:8000` with Swagger UI at `/docs`
- **(Phase 2)** Vite frontend on `localhost:5173`

### Verify It's Working

```bash
curl http://localhost:8000/health
# Response: {"status":"ok"}
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser to see the interactive Swagger UI.

---

## API Endpoints

### Authentication

#### Register a User
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "John Doe"
  }'
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2026-07-06T08:00:00.000000"
}
```

#### Login (Get JWT Token)
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get Current User (Requires Token)
```bash
TOKEN="your_access_token_here"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/me
```

---

### Products & Categories

#### List Categories
```bash
curl http://localhost:8000/categories
```

#### Create Category
```bash
curl -X POST http://localhost:8000/categories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Electronics",
    "description": "Electronic devices"
  }'
```

#### List Products (with Pagination & Filtering)
```bash
# Get first 10 products
curl "http://localhost:8000/products?skip=0&limit=10"

# Filter by category
curl "http://localhost:8000/products?category_id=1"

# Combine pagination and filtering
curl "http://localhost:8000/products?skip=0&limit=10&category_id=1"
```

**Response:**
```json
{
  "items": [...],
  "total": 25,
  "page": 1,
  "page_size": 10,
  "total_pages": 3
}
```

#### Create Product
```bash
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 999.99,
    "stock": 5,
    "category_id": 1
  }'
```

#### Get Product by ID
```bash
curl http://localhost:8000/products/1
```

#### Update Product
```bash
curl -X PUT http://localhost:8000/products/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gaming Laptop",
    "price": 1299.99
  }'
```

#### Delete Product
```bash
curl -X DELETE http://localhost:8000/products/1
```

---

### Shopping Cart

**All cart endpoints require authentication. Use the token from login:**

#### View Cart
```bash
TOKEN="your_token"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/cart
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "quantity": 2,
      "product": {
        "id": 1,
        "name": "Laptop",
        "price": 999.99,
        ...
      }
    }
  ],
  "total_price": 1999.98
}
```

#### Add Item to Cart
```bash
curl -X POST http://localhost:8000/cart/items \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```

#### Update Item Quantity
```bash
curl -X PUT http://localhost:8000/cart/items/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 5
  }'
```

#### Remove Item from Cart
```bash
curl -X DELETE http://localhost:8000/cart/items/1 \
  -H "Authorization: Bearer $TOKEN"
```

#### Clear Cart
```bash
curl -X DELETE http://localhost:8000/cart \
  -H "Authorization: Bearer $TOKEN"
```

---

### Orders & Checkout

**All order endpoints require authentication.**

#### Checkout (Convert Cart to Order)
```bash
curl -X POST http://localhost:8000/checkout \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "total_price": 1999.98,
  "status": "completed",
  "created_at": "2026-07-06T08:30:00.000000",
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "quantity": 2,
      "price_at_purchase": 999.99,
      "product": {...}
    }
  ]
}
```

**Note:** Cart is automatically cleared after checkout.

#### View Order History
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/orders
```

**Response:**
```json
{
  "items": [...],
  "total": 3
}
```

#### Get Order Details
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/orders/1
```

---

## Database Migrations

Migrations are automatically applied when you run the API. To manually manage migrations:

### View Migration Status
```bash
docker compose run api alembic current
```

### Create New Migration (after modifying models.py)
```bash
docker compose run api alembic revision --autogenerate -m "Description of changes"
docker compose run api alembic upgrade head
```

### Rollback Last Migration
```bash
docker compose run api alembic downgrade -1
```

---

## Running Tests

Run all tests:
```bash
docker compose run api pytest test_api.py -v
```

Run specific test:
```bash
docker compose run api pytest test_api.py::test_register_user -v
```

Run with coverage:
```bash
docker compose run api pytest test_api.py --cov=. --cov-report=html
```

---

## Project Structure

```
.
├── docker-compose.yml          # Orchestrates API and PostgreSQL
├── api/
│   ├── main.py                 # FastAPI app and routers
│   ├── models.py               # SQLAlchemy ORM models
│   ├── schemas.py              # Pydantic request/response schemas
│   ├── routes.py               # Product & category endpoints
│   ├── auth.py                 # Password hashing and JWT functions
│   ├── auth_routes.py          # Auth endpoints (register, login)
│   ├── cart_routes.py          # Cart endpoints
│   ├── order_routes.py         # Checkout & orders endpoints
│   ├── database.py             # SQLAlchemy setup
│   ├── config.py               # Environment variables
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile              # API container image
│   ├── alembic/                # Database migrations
│   ├── test_api.py             # Pytest suite (26 tests)
│   └── .env                    # Database credentials (local)
└── web/                        # (Phase 2) Vite frontend
```

---

## Environment Variables

Edit `api/.env` to change:

```
DATABASE_URL=postgresql://shopping_user:shopping_password@db:5432/shopping_db
SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Common Issues & Troubleshooting

### `Failed to connect to database`
- Ensure Docker Desktop is running
- Check `docker ps` to see if the `db` container is healthy
- Run `docker compose logs db` to see database logs

### `Port 8000 already in use`
```bash
# Find what's using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>

# Or change the port in docker-compose.yml:
ports:
  - "8001:8000"  # Map to 8001 instead
```

### `CORS errors in browser`
- Frontend must run at `http://localhost:5173` (Phase 2)
- API automatically allows this origin in `main.py`
- Check browser console for exact error

### `Migrations not applying`
```bash
# Check migration status
docker compose run api alembic current

# Force re-apply migrations
docker compose run api alembic stamp head
docker compose run api alembic upgrade head
```

### `JWT token expired or invalid`
- Token expiration is 30 minutes (set in `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Log in again to get a fresh token
- Make sure Authorization header is: `Bearer <token>` (with space)

### `Empty database (no products)`
- Use Swagger UI at `/docs` to create products
- Or use curl requests above
- Products won't show without the category first

---

## What You Learned

✅ **Backend Architecture:** REST API design with FastAPI  
✅ **Database:** SQLAlchemy ORM and Alembic migrations  
✅ **Authentication:** JWT tokens and password hashing  
✅ **Testing:** Pytest with fixtures and test isolation  
✅ **DevOps:** Docker & Docker Compose for local development  
✅ **API Design:** Pagination, filtering, relationships  

---

## Next Steps

- **Phase 2:** Build a Vite frontend in vanilla JavaScript
- **Phase 3:** Convert frontend to TypeScript
- **Bonus Ideas:**
  - Add Redis for caching or sessions
  - Deploy to cloud (AWS, Heroku, DigitalOcean)
  - Add product reviews and ratings
  - Implement search with Elasticsearch
  - Add admin dashboard

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review test cases in `test_api.py` for API usage examples
3. Visit [FastAPI docs](https://fastapi.tiangolo.com) for framework questions
4. Check [SQLAlchemy docs](https://docs.sqlalchemy.org) for database questions

---

**Built with ❤️ as a learning project**
