# Shopping Cart Application

A complete full-stack learning project with a REST API backend and interactive frontend, all running in Docker.

**Tech Stack:**
- **Backend:** Python 3.12, FastAPI, SQLAlchemy, Alembic
- **Database:** PostgreSQL 16
- **Frontend:** Vanilla JavaScript, Vite, HTML5, CSS3
- **Containerization:** Docker & Docker Compose

**Architecture:**
- FastAPI REST API with JWT authentication
- PostgreSQL database with migrations
- Vanilla JS frontend (no frameworks)
- Docker Compose orchestration

---

## Quick Start

### Prerequisites

- Docker Desktop (running)
- Git

### Run Everything with One Command

```bash
docker compose up --build
```

This starts three services:
- **PostgreSQL** on `localhost:5432` (database)
- **FastAPI API** on `localhost:8000` (REST API)
- **Vite frontend** on `localhost:5173` (interactive UI)

### Access the Application

| Service | URL | Purpose |
|---------|-----|---------|
| **Shopping App** | http://localhost:5173 | Frontend UI (register, login, shop, checkout) |
| **API Docs** | http://localhost:8000/docs | Swagger UI (test endpoints directly) |
| **API Health** | http://localhost:8000/health | Health check endpoint |

### Quick Verification

```bash
# Check API is running
curl http://localhost:8000/health
# Response: {"status":"ok"}

# View API documentation
open http://localhost:8000/docs

# Open shopping app
open http://localhost:5173
```

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

## Phase 2: Frontend (Vanilla JavaScript + Vite)

The `web/` folder contains a complete shopping cart UI built with vanilla JavaScript and Vite.

### Frontend Tech Stack
- **Vite:** Modern build tool with hot module reload
- **Vanilla JavaScript:** No frameworks—just DOM APIs and Fetch
- **CSS3:** Responsive design with mobile-first approach
- **Fetch API:** HTTP client for REST API calls

### Frontend Features

**User Authentication:**
- Register new account
- Login with email/password
- Session persistence (localStorage token)
- Logout clears token and cart
- Auto-login after registration

**Shopping Experience:**
- Browse products from database
- Filter by category
- Add items to cart
- Update quantities
- Remove items
- View cart totals (subtotal + tax)

**Checkout:**
- Place order (converts cart to order)
- Order confirmation with details
- Clear cart after checkout
- View past orders with items

**UI/UX Polish:**
- Responsive layout (mobile, tablet, desktop)
- In-page success/error messages (no alerts)
- Button loading states during API calls
- Dark mode support
- Touch-friendly controls
- Smooth animations and transitions
- Form validation and error handling

### Running the Frontend

Everything runs with `docker compose up --build`. Then:

**Frontend URL:** http://localhost:5173

**API Docs:** http://localhost:8000/docs (test endpoints here)

### Key Files

| File | Purpose |
|------|---------|
| `web/index.html` | HTML structure for UI |
| `web/src/main.js` | App state, event handlers, DOM updates |
| `web/src/api.js` | API wrapper functions (fetch calls) |
| `web/src/style.css` | Responsive CSS with dark mode |
| `web/vite.config.js` | Vite config (host, port, hot reload) |

### Frontend Architecture

**Separation of Concerns:**
- `api.js` — All API calls (encapsulated, reusable)
- `main.js` — State management and UI logic
- `style.css` — Presentation (responsive, accessible)
- `index.html` — Semantic structure

**State Management:**
```javascript
const state = {
  isLoggedIn: false,
  user: null,
  token: null,
  cart: [],
  products: [],
  currentOrder: null,
}
```

**Session Persistence:**
- JWT token stored in `localStorage`
- Auto-restored on page load
- Token sent as `Authorization: Bearer <token>` header

### Testing the Frontend

**Full shopping flow:**
1. Open http://localhost:5173
2. Click "Login" → Register new account
3. Browse products (loaded from `/products` endpoint)
4. Add items to cart
5. View cart totals
6. Checkout → see order confirmation
7. Click "View Order History" → see past orders
8. Logout → token cleared, cart emptied

**Responsive testing:**
- Resize browser to mobile (< 600px) → single-column layout
- Resize to tablet (600-1024px) → two-column grid
- Full desktop (> 1024px) → multi-column with sidebar

### API Integration Points

Frontend calls these endpoints:

| Endpoint | Purpose |
|----------|---------|
| `POST /register` | Create account |
| `POST /login` | Get JWT token |
| `GET /me` | Get current user |
| `GET /products` | Fetch product list |
| `POST /cart/items` | Add to cart |
| `PUT /cart/items/{id}` | Update quantity |
| `DELETE /cart/items/{id}` | Remove item |
| `GET /cart` | View cart |
| `POST /checkout` | Place order |
| `GET /orders` | View order history |

---

## What You Learned

✅ **Backend Architecture:** REST API design with FastAPI  
✅ **Database:** SQLAlchemy ORM and Alembic migrations  
✅ **Authentication:** JWT tokens and password hashing  
✅ **Testing:** Pytest with fixtures and test isolation  
✅ **DevOps:** Docker & Docker Compose for local development  
✅ **API Design:** Pagination, filtering, relationships  
✅ **Frontend Development:** Vanilla JS without frameworks  
✅ **UI/UX:** Responsive design, state management, form handling  
✅ **API Integration:** Fetch, token management, error handling  

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
