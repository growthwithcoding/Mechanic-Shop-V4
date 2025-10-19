# SQL Scripts for Mechanic Shop V4

This folder contains SQL scripts for database setup and seeding.

## ⚠️ Important: Two Separate Databases

This project uses **TWO SEPARATE databases**:

1. **`mechanic_shop_v4`** - DEVELOPMENT/PRODUCTION Database
   - Used when running the API normally: `python app.py`
   - Populated with `seed_sample_data.sql` for testing
   - Data persists between API runs
   - Login works with: `alice.johnson@email.com` / `password123`

2. **`mechanic_shop_v4_test`** - UNIT TEST Database
   - Used ONLY when running unit tests: `python -m unittest`
   - Created by `create_test_database.sql`
   - **Does NOT use seed_sample_data.sql**
   - Tests create their own temporary data
   - Data is wiped after each test
   - Login uses test-specific credentials

---

## Files

### 1. recreate_database.sql
**Purpose**: Drops and recreates the `mechanic_shop_v4` database

**When to use**: 
- Initial setup
- When you need a fresh database
- After major schema changes

**How to run**:
```bash
mysql -u root -p < SQL/recreate_database.sql
```

**After running**: Execute Flask migrations to create tables
```bash
flask db upgrade
```

---

### 2. seed_sample_data.sql
**Purpose**: Populates the **DEVELOPMENT database** with sample data for manual testing

**Database**: `mechanic_shop_v4` (NOT the test database!)

**Includes**:
- 5 Sample Customers (with working passwords!)
- 6 Sample Vehicles
- 5 Sample Mechanics
- 10 Sample Services
- 12 Sample Parts (Inventory items)
- 8 Specializations
- 6 Sample Service Tickets
- Mechanic certifications
- Service packages
- And more...

**When to use**:
- After running migrations on development database
- For manual API testing with Postman/Swagger
- To quickly populate development database with realistic data
- **NOT needed for unit tests** (they create their own data)

**How to run**:
```bash
# Make sure database and tables exist first
flask db upgrade

# Then seed the data (DEVELOPMENT database only)
mysql -u root -p mechanic_shop_v4 < SQL/seed_sample_data.sql
```

**Test Login Credentials** (after seeding):
- Email: `alice.johnson@email.com`
- Password: `password123`
- (All seeded customers use the same password)

**⚠️ Password Hash Note**: The seed file uses werkzeug scrypt hashes compatible with the application's password checking. Do NOT use bcrypt hashes!

---

### 3. fix_user_permissions.sql
**Purpose**: Grants necessary privileges to database user

**When to use**:
- When you encounter "Access Denied" errors
- After creating a new database user
- If migrations fail due to permissions

**How to run**:
```bash
mysql -u root -p < SQL/fix_user_permissions.sql
```

**Important**: Update the username/host in the script if not using 'root'@'localhost'

### 3. create_test_database.sql
**Purpose**: Creates the **TEST database** for unit tests

**Database**: `mechanic_shop_v4_test` (separate from development!)

**When to use**:
- Before running unit tests for the first time
- Only needs to be run once
- Unit tests will create/destroy tables automatically

**How to run**:
```bash
mysql -u root -p < SQL/create_test_database.sql
```

**Note**: You do NOT need to run migrations or seed data for the test database. Unit tests handle this automatically.

---

### 4. fix_user_permissions.sql
**Purpose**: Grants necessary privileges to database user

**When to use**:
- When you encounter "Access Denied" errors
- After creating a new database user
- If migrations fail due to permissions

**How to run**:
```bash
mysql -u root -p < SQL/fix_user_permissions.sql
```

**Important**: Update the username/host in the script if not using 'root'@'localhost'

---

## Complete Setup Workflow

### For Development/Manual Testing:

**Windows PowerShell (if MySQL is in PATH):**
```powershell
# 1. Create/Recreate DEVELOPMENT Database
Get-Content SQL\recreate_database.sql | mysql -u root -p

# 2. Run Migrations (creates all tables)
$env:FLASK_APP = "app.py"
flask db upgrade

# 3. Seed Sample Data (DEVELOPMENT database)
Get-Content SQL\seed_sample_data.sql | mysql -u root -p mechanic_shop_v4

# 4. Start the API
python app.py
```

**Windows PowerShell (if MySQL is NOT in PATH):**
```powershell
# 1. Open MySQL Workbench or MySQL Command Line Client
# 2. Run the SQL files manually:
#    - Open SQL\recreate_database.sql and execute it
#    - Close and reconnect to the new database

# 3. Run Migrations (creates all tables)
$env:FLASK_APP = "app.py"
flask db upgrade

# 4. Seed Sample Data - Open MySQL Workbench/Command Line Client
#    - Connect to mechanic_shop_v4 database
#    - Open SQL\seed_sample_data.sql
#    - Execute the entire file

# 5. Start the API
python app.py

# 6. Test with seeded credentials
# Login at: POST /auth/login
# Email: alice.johnson@email.com
# Password: password123
```

**Alternative: Add MySQL to PATH (Windows):**
```powershell
# Find your MySQL installation (usually in Program Files)
# Example: C:\Program Files\MySQL\MySQL Server 8.0\bin

# Add to PATH temporarily (current session only):
$env:Path += ";C:\Program Files\MySQL\MySQL Server 8.0\bin"

# Then run the commands above
Get-Content SQL\recreate_database.sql | mysql -u root -p
```

**Windows CMD or Mac/Linux:**
```bash
# 1. Create/Recreate DEVELOPMENT Database
mysql -u root -p < SQL/recreate_database.sql

# 2. Run Migrations (creates all tables)
set FLASK_APP=app.py  # Windows CMD
# export FLASK_APP=app.py  # Mac/Linux
flask db upgrade

# 3. Seed Sample Data (DEVELOPMENT database)
mysql -u root -p mechanic_shop_v4 < SQL/seed_sample_data.sql

# 4. (Optional) Fix Permissions if needed
mysql -u root -p < SQL/fix_user_permissions.sql

# 5. Start the API
python app.py

# 6. Test with seeded credentials
# Login at: POST /auth/login
# Email: alice.johnson@email.com
# Password: password123
```

### For Unit Testing:

**Windows PowerShell (if MySQL is in PATH):**
```powershell
# 1. Create TEST Database (one-time setup)
Get-Content SQL\create_test_database.sql | mysql -u root -p

# 2. Run Unit Tests (they handle everything else)
python -m unittest discover tests -v
```

**Windows PowerShell (if MySQL is NOT in PATH):**
```powershell
# 1. Open MySQL Workbench or MySQL Command Line Client
#    - Open SQL\create_test_database.sql
#    - Execute it to create mechanic_shop_v4_test database

# 2. Run Unit Tests (they handle everything else)
python -m unittest discover tests -v

# Note: Tests create their own temporary data
# No seed data or migrations needed for test database!
```

**Windows CMD or Mac/Linux:**
```bash
# 1. Create TEST Database (one-time setup)
mysql -u root -p < SQL/create_test_database.sql

# 2. Run Unit Tests (they handle everything else)
python -m unittest discover tests -v

# Note: Tests create their own temporary data
# No seed data or migrations needed for test database!
```

---

## Testing Data via API

After seeding, use these API endpoints to complete the setup:

### 1. Register a Customer
```bash
POST /auth/register
{
  "first_name": "Test",
  "last_name": "User",
  "email": "test@example.com",
  "password": "password123",
  "phone": "555-9999",
  "address": "123 Test St",
  "city": "Denver",
  "state": "CO",
  "postal_code": "80201"
}
```

### 2. Login to Get Token
```bash
POST /auth/login
{
  "email": "test@example.com",
  "password": "password123"
}
```

### 3. Create a Vehicle
```bash
POST /customers/1/vehicles
Authorization: Bearer {token}
{
  "vin": "1HGCM82633A123456",
  "make": "Honda",
  "model": "Accord",
  "year": 2020,
  "color": "Blue"
}
```

### 4. Create a Service Ticket
```bash
POST /service-tickets
Authorization: Bearer {token}
{
  "vehicle_id": 1,
  "customer_id": 1,
  "status": "open",
  "problem_description": "Oil change needed",
  "odometer_miles": 50000,
  "priority": 2
}
```

### 5. Assign Mechanic to Ticket
```bash
PUT /service-tickets/1/assign-mechanic/1
Authorization: Bearer {token}
{
  "role": "Lead Technician",
  "minutes_worked": 0
}
```

### 6. Add Part to Ticket
```bash
POST /service-tickets/1/parts/1
Authorization: Bearer {token}
{
  "quantity_used": 1,
  "markup_percentage": 30.0,
  "warranty_months": 6
}
```

---

## Sample Data Overview

### Mechanics
- **John Smith** - ASE Master, Engine Specialist
- **Sarah Johnson** - Brake Specialist, ASE Master
- **Mike Williams** - Transmission Specialist
- **Emily Davis** - Electrical Systems, Hybrid/EV Certified
- **Robert Brown** - Suspension & Steering Expert

### Services
- Oil Change ($35.00)
- Tire Rotation ($25.00)
- Brake Inspection ($50.00)
- Brake Pad Replacement ($150.00)
- Engine Diagnostic ($85.00)
- And 5 more...

### Parts
- Engine Oil 5W-30 (50 in stock)
- Oil Filter (75 in stock)
- Brake Pad Sets (45 total)
- Brake Rotors (27 total)
- And 8 more...

---

## Troubleshooting

### "Database does not exist"
Run `recreate_database.sql` first

### "Table doesn't exist"
Run `flask db upgrade` after creating database

### "Access denied"
Run `fix_user_permissions.sql` with appropriate user credentials

### "No sample data"
Run `seed_sample_data.sql` after migrations

### "Password authentication failed"
Update database connection string in `config.py` or environment variables

---

For more information, see the main README.md in the project root.
