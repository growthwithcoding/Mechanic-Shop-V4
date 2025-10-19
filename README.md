# Mechanic Shop Management API - V4

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.1+-green.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-14+-blue.svg)
![Deploy](https://img.shields.io/badge/deploy-render-success.svg)

A production-ready RESTful API for managing automotive repair shop operations with comprehensive Swagger documentation, automated testing, JWT authentication, and full CI/CD pipeline deployed on Render.

## 👨‍💻 Author

**Austin Carlson** - *#growthwithcoding*

- 🔗 GitHub: [https://github.com/growthwithcoding](https://github.com/growthwithcoding)
- 💼 LinkedIn: [https://www.linkedin.com/in/austin-carlson-720b65375/](https://www.linkedin.com/in/austin-carlson-720b65375/)

---

## 🚀 Live Deployment

- **Live API:** https://mechanic-shop-v4.onrender.com
- **API Documentation:** https://mechanic-shop-v4.onrender.com/apidocs
- **GitHub Repository:** https://github.com/growthwithcoding/Mechanic-Shop-V4
- **Health Check:** https://mechanic-shop-v4.onrender.com/

---

## 🎯 Deployment Assignment Requirements

### Assignment: API Deployment and CI/CD Pipeline
**Instructor:** Dylan Katina

#### ✅ ALL REQUIREMENTS COMPLETED

**Production Setup:**
- ✅ **PostgreSQL Database on Render** - Hosted and configured
- ✅ **Production Configuration** - `ProductionConfig` with environment variables
- ✅ **Dependencies** - gunicorn, psycopg (v3), python-dotenv installed
- ✅ **Environment Variables** - Secure `.env` file with `.env.example` template
- ✅ **.gitignore** - `.env` excluded from version control
- ✅ **OS Package Usage** - `os.environ.get()` for secure config retrieval
- ✅ **Entry Point** - `flask_app.py` (renamed from `app.py`)
- ✅ **ProductionConfig** - Loaded via `FLASK_CONFIG` environment variable
- ✅ **app.run() Removed** - Gunicorn handles WSGI serving

**Render Deployment:**
- ✅ **GitHub Push** - Code pushed to repository
- ✅ **Web Service Deployed** - Running on Render with auto-deployments
- ✅ **Environment Variables** - Configured in Render dashboard
- ✅ **Swagger Host Updated** - `mechanic-shop-v4.onrender.com` (no https://)
- ✅ **Swagger Schemes** - Changed to `["https"]` only

**CI/CD Pipeline:**
- ✅ **.github/workflows/** - Directory and `main.yaml` created
- ✅ **Workflow Name** - "CI/CD Pipeline for Mechanic Shop API"
- ✅ **Triggers** - Push to main, pull requests
- ✅ **Build Job** - Dependency installation and verification
- ✅ **Test Job** - Runs pytest with PostgreSQL database
- ✅ **Deploy Job** - Auto-deploys to Render (depends on: test)

#### 📊 Submission Information

**For Instructor:**
- **Live API URL:** https://mechanic-shop-v4.onrender.com
- **GitHub Repository:** https://github.com/growthwithcoding/Mechanic-Shop-V4
- **Status:** ✅ Fully deployed and operational
- **Database:** PostgreSQL 14+ on Render
- **Runtime:** Python 3.11 with Gunicorn

---

## 🌐 Live API Usage

### Quick Start

**1. Access Interactive API Documentation:**
```
https://mechanic-shop-v4.onrender.com/apidocs
```

**2. Health Check:**
```bash
curl https://mechanic-shop-v4.onrender.com/
```

**3. Seed Database (One-Time):**
```bash
curl -X POST https://mechanic-shop-v4.onrender.com/admin/seed-database
```

**4. Login:**
```bash
curl -X POST "https://mechanic-shop-v4.onrender.com/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"alice.johnson@email.com","password":"password123"}'
```

**5. Use JWT Token:**
```bash
curl -X GET "https://mechanic-shop-v4.onrender.com/customers" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Sample Credentials

Password for all accounts: `password123`

- alice.johnson@email.com
- bob.smith@email.com
- carol.williams@email.com

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

**Location:** `.github/workflows/main.yaml`

**Triggers:**
- Push to `main` branch
- Pull requests to `main`

**Jobs:**

1. **Build** - Python 3.11 setup, dependency installation
2. **Test** - Run pytest with PostgreSQL test database
3. **Deploy** - Auto-deploy to Render (needs: test)

**Features:**
- Automated testing before deployment
- PostgreSQL test database service
- Render API integration for deployments
- Branch protection with required tests

---

## ✨ Project Features

### Core Functionality

- **JWT Authentication** - Secure token-based auth with 1-hour expiration
- **Rate Limiting** - API protection (register: 3/hr, login: 5/min)
- **Response Caching** - 5-minute cache on frequently accessed endpoints
- **Swagger Documentation** - Interactive API testing at `/apidocs`
- **Comprehensive Testing** - 106 tests with unittest framework
- **Error Handling** - Detailed error responses with unique tracking IDs

### Advanced Features

- **Pagination** - Efficient data retrieval (default 10 per page)
- **Sorting** - Mechanics by activity, parts by stock level
- **Bulk Operations** - Add/remove multiple mechanics from tickets
- **Inventory Management** - Automatic stock tracking with low-stock alerts
- **Many-to-Many Relationships** - Tickets ↔ Mechanics, Tickets ↔ Parts
- **Automatic Migrations** - Database updates run on deployment

---

## 📚 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth | Rate Limit |
|--------|----------|-------------|------|------------|
| POST | `/auth/register` | Register new customer | No | 3/hour |
| POST | `/auth/login` | Login, get JWT token | No | 5/min |
| GET | `/auth/me` | Get current user info | Yes | - |

### Customers

| Method | Endpoint | Description | Auth | Pagination |
|--------|----------|-------------|------|-----------|
| GET | `/customers` | List all customers | Yes | Yes |
| GET | `/customers/<id>` | Get customer details | Yes | - |
| PUT | `/customers/<id>` | Update customer | Yes | - |
| DELETE | `/customers/<id>` | Delete customer | Yes | - |

### Mechanics

| Method | Endpoint | Description | Auth | Cached |
|--------|----------|-------------|------|--------|
| POST | `/mechanics` | Create mechanic | Yes | - |
| GET | `/mechanics` | List all mechanics | Yes | 5 min |
| GET | `/mechanics/<id>` | Get mechanic details | Yes | - |
| GET | `/mechanics/by-activity` | Sort by ticket count | Yes | - |
| PUT | `/mechanics/<id>` | Update mechanic | Yes | - |
| DELETE | `/mechanics/<id>` | Delete mechanic | Yes | - |

### Service Tickets

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/service-tickets` | Create ticket | Yes |
| GET | `/service-tickets` | List all tickets | Yes |
| GET | `/service-tickets/<id>` | Get ticket details | Yes |
| PUT | `/service-tickets/<id>` | Update ticket | Yes |
| PUT | `/service-tickets/<id>/edit` | Bulk edit mechanics | Yes |
| POST | `/service-tickets/<id>/parts/<part_id>` | Add part to ticket | Yes |

### Inventory

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/inventory` | Create part | Yes |
| GET | `/inventory` | List all parts | Yes |
| GET | `/inventory?low_stock=true` | Low-stock parts | Yes |
| GET | `/inventory/<id>` | Get part details | Yes |
| PUT | `/inventory/<id>` | Update part | Yes |
| PATCH | `/inventory/<id>/adjust-quantity` | Adjust quantity | Yes |

---

## 🗄️ Database Schema

### Core Models

- **Customer** - User accounts with authentication
- **Vehicle** - Customer vehicles
- **Mechanic** - Shop staff
- **ServiceTicket** - Work orders
- **Part** - Inventory items

### Junction Tables

- **TicketMechanic** - Mechanics assigned to tickets
- **TicketPart** - Parts used in tickets

### Relationships

```
Customer 1→M Vehicle
Customer 1→M ServiceTicket
ServiceTicket M→M Mechanic (via TicketMechanic)
ServiceTicket M→M Part (via TicketPart)
```

---

## 💻 Local Development

### Prerequisites

- Python 3.11+
- MySQL 8.0+ OR PostgreSQL 14+
- Git

### Setup

```bash
# 1. Clone repository
git clone https://github.com/growthwithcoding/Mechanic-Shop-V4.git
cd Mechanic-Shop-V4

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env with your database credentials

# 5. Run migrations
flask db upgrade

# 6. Start development server
python app.py

# 7. Access Swagger docs
# http://127.0.0.1:5000/apidocs
```

### Environment Variables

Create `.env` file:

```env
# Flask Configuration
FLASK_CONFIG=development

# Database (MySQL for local development)
DEV_DATABASE_URL=mysql+mysqlconnector://root:password@127.0.0.1/mechanic_shop_v4

# Security Keys
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
```

---

## 🧪 Testing

### Run Tests

```bash
# Create test database first
python create_test_db.py

# Run all tests
python -m unittest discover tests

# Run with verbose output
python -m unittest discover tests -v

# Run specific test file
python -m unittest tests.test_customer -v
```

### Test Coverage

- **106 total tests** across 5 test suites
- Auth, Customer, Mechanic, Service Ticket, Inventory
- Positive and negative test cases
- JWT authentication testing
- Rate limiting validation

---

## 🔧 Technologies

**Framework & Core:**
- Flask 3.1+ - Web framework
- SQLAlchemy 2.0+ - ORM
- Flask-Migrate - Database migrations
- Gunicorn - WSGI server (production)

**Authentication & Security:**
- Flask-JWT-Extended - JWT tokens
- Werkzeug - Password hashing
- Flask-Limiter - Rate limiting

**API & Documentation:**
- Flasgger - Swagger/OpenAPI documentation
- Flask-Marshmallow - Object serialization

**Testing & CI/CD:**
- unittest - Python testing framework
- GitHub Actions - CI/CD pipeline
- pytest - Test runner (alternative)

**Database:**
- MySQL 8.0+ (local development)
- PostgreSQL 14+ (production on Render)

**Deployment:**
- Render - Cloud platform
- PostgreSQL - Managed database

---

## 📁 Project Structure

```
Mechanic-Shop-V4/
├── application/           # Main app package
│   ├── __init__.py       # Factory pattern, Swagger config
│   ├── extensions.py     # Flask extensions
│   ├── models.py         # SQLAlchemy models
│   └── blueprints/       # Feature modules
│       ├── auth/         # Authentication
│       ├── customer/     # Customer management
│       ├── mechanic/     # Mechanic management
│       ├── service_ticket/ # Ticket system
│       └── inventory/    # Parts inventory
├── tests/                # Test suite (106 tests)
├── migrations/           # Database migrations
├── .github/workflows/    # CI/CD pipeline
├── flask_app.py         # Production entry point
├── app.py               # Development entry point
├── config.py            # Configuration classes
├── seed_data.json       # Sample data for seeding
└── requirements.txt     # Dependencies
```

---

## 📖 Additional Documentation

- **Swagger UI:** https://mechanic-shop-v4.onrender.com/apidocs
- **SWAGGER_DOCUMENTATION.md** - Detailed Swagger implementation
- **TESTING.md** - Comprehensive testing guide
- **ERROR_HANDLING.md** - Error handling documentation
- **Postman/** - API testing collections

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/NewFeature`)
3. Commit changes (`git commit -m 'Add NewFeature'`)
4. Push to branch (`git push origin feature/NewFeature`)
5. Open Pull Request

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/growthwithcoding/Mechanic-Shop-V4/issues)
- **LinkedIn:** [Austin Carlson](https://www.linkedin.com/in/austin-carlson-720b65375/)

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🎓 Academic Use

This project was developed for:
- **Course:** Advanced API Development
- **Instructor:** Dylan Katina
- **Focus:** V4 - Documentation, Testing & Deployment

Students: Use as reference only. Write your own code to learn effectively.

---

**Built with ❤️ by Austin Carlson** | *#growthwithcoding*

**Version 4.0** - Production Deployment
