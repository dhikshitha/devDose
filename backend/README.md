# Tech Learning Companion - Backend API

## Phase 1: Authentication System

This Flask backend provides the foundation for the Tech Learning Companion application with a complete authentication system.

### Features
- User registration and login
- JWT-based authentication
- Password hashing with bcrypt
- User profile management
- Input validation
- CORS support for frontend integration

### Project Structure
```
backend/
├── app.py              # Flask application factory
├── config.py           # Configuration settings
├── models/
│   └── user.py        # User model with authentication
├── routes/
│   └── auth.py        # Authentication endpoints
├── utils/
│   └── auth_utils.py  # JWT and validation utilities
└── requirements.txt    # Python dependencies
```

### Setup Instructions

1. **Set up PostgreSQL Database**

Option A: Using PostgreSQL locally
```bash
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql

# Create databases
createdb tech_learning_dev
createdb tech_learning_test
createdb tech_learning_prod
```

Option B: Using Docker (recommended)
```bash
docker run --name tech-learning-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=tech_learning_dev \
  -p 5432:5432 \
  -d postgres:16-alpine
```

2. **Create a virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your PostgreSQL configuration
```

5. **Initialize the database with migrations**
```bash
# Initialize migrations
flask db init

# Create first migration
flask db migrate -m "Initial migration"

# Apply migrations
flask db upgrade
```

Alternative: Initialize without migrations
```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
```

6. **Run the development server**
```bash
python app.py
# or
flask run
```

The API will be available at `http://localhost:5000`

### API Endpoints

#### Authentication
- `POST /api/auth/register` - Create a new user account
- `POST /api/auth/login` - Login with username/email and password
- `POST /api/auth/logout` - Logout (requires authentication)
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/profile` - Get current user profile
- `PUT /api/auth/profile` - Update user profile
- `POST /api/auth/change-password` - Change user password

#### Health Check
- `GET /api/health` - Check API status

### Request/Response Examples

#### Register
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123"
  }'
```

#### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "login": "testuser",
    "password": "SecurePass123"
  }'
```

#### Get Profile (Authenticated)
```bash
curl -X GET http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Testing

Run tests with pytest:
```bash
pytest
```

### Next Phase
Phase 2 will add the content delivery system with daily tech concepts.