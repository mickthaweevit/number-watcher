# 🎯 NumWatch - Thai Lottery Analysis System

A comprehensive Thai lottery number analysis and tracking system with real-time data import, pattern analysis, and user management.

## 🌟 Features

### 🔐 Authentication & User Management
- **Secure JWT Authentication** (no expiration for convenience)
- **Invite-based Registration** system
- **Admin Panel** for user and invite code management
- **Thai Language Interface** throughout the application

### 📊 Lottery Data Management
- **Dual API Support** (V1 & V2 formats)
- **Real-time Data Import** from external APIs
- **Automated Scheduler** for regular data updates
- **Buddhist Calendar Support** (พ.ศ. format)
- **Multiple Game Types** including HNLOCAL

### 🎲 Pattern Analysis Dashboard
- **3-Up Pattern Analysis** with multiple betting strategies:
  - เบิ้ลหน้า (First Two Same)
  - หาม (First & Last Same) 
  - เบิ้ลหลัง (Last Two Same)
- **Profit/Loss Calculations** with customizable bet amounts
- **Monthly Statistics** breakdown
- **Visual Pattern Highlighting** in results table

### 👤 Profile Management
- **Auto-load Profiles** on selection (no manual load button)
- **Split Save Options**:
  - บันทึก (Save Current) - Update existing profile
  - บันทึกใหม่ (Save as New) - Create new profile
- **Unsaved Changes Protection**:
  - Visual indicators (orange border, asterisk)
  - Browser exit warnings
  - Route navigation guards
- **Smart Button States** (disabled when no changes)

### 📱 Mobile-Responsive Design
- **Thai-optimized Interface** for local users
- **Responsive Layout** for mobile devices
- **Touch-friendly Navigation**
- **Optimized Table Scrolling**

## 🛠️ Tech Stack

### Backend
- **FastAPI** (Python) - High-performance API framework
- **PostgreSQL** - Primary database
- **SQLAlchemy** - ORM with Alembic migrations
- **JWT Authentication** - Secure token-based auth
- **APScheduler** - Automated data import scheduling
- **Async/Await** - Non-blocking operations

### Frontend
- **Vue.js 3** - Progressive JavaScript framework
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Vue Router** - Client-side routing
- **Axios** - HTTP client with interceptors

### Infrastructure
- **Docker** - Containerized deployment
- **GitHub Actions** - CI/CD pipeline
- **Environment-based Configuration**

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.9+ (for local development)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/mickthaweevit/number-watcher.git
cd number-watcher
```

2. **Set up environment variables**
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:password@localhost:5432/numwatch
EXTERNAL_API_URL=https://api.example.com
EXTERNAL_API_URL_V2=https://apiv2.example.com
CORS_ORIGINS=http://localhost:5173

# Frontend (.env)
VITE_API_URL=http://localhost:8000
```

3. **Run with Docker Compose**
```bash
docker-compose up -d
```

4. **Create admin user**
```bash
curl -X POST "http://localhost:8000/create-admin"
```

5. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📖 API Documentation

### Authentication Endpoints
- `POST /auth/register` - Register with invite code
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info

### Data Import Endpoints
- `POST /import-live-data-v2` - Import current day data
- `POST /import-date-range-v2` - Import date range (YYYYMMDD format)
- `GET /games?source=new` - Get games from V2 API
- `GET /results?source=new` - Get results from V2 API

### Profile Management
- `GET /profiles` - Get user profiles
- `POST /profiles` - Create new profile
- `PUT /profiles/{id}` - Update existing profile
- `DELETE /profiles/{id}` - Delete profile

### Admin Endpoints
- `POST /admin/invite-codes` - Create invite codes
- `GET /admin/users` - List all users
- `GET /scheduler/status` - Check scheduler status

## 🎯 Usage Guide

### Setting Up Analysis
1. **Login** with your credentials
2. **Select API Source** (แหล่ง 1 or แหล่ง 2)
3. **Configure Global Settings**:
   - Set bet amount (จำนวนเงินแทง)
   - Choose patterns (รูปแบบที่เลือก)
4. **Add Games** to analyze
5. **Save Profile** for future use

### Pattern Analysis
- **เบิ้ลหน้า**: Numbers like 113, 225, 882 (first two digits same)
- **หาม**: Numbers like 040, 747, 202 (first and last digits same)
- **เบิ้ลหลัง**: Numbers like 200, 877, 399 (last two digits same)

### Reading Results
- **Green numbers**: Pattern matches (wins)
- **Red/Blue/Yellow highlights**: Different pattern types
- **Statistics panel**: Win/loss ratios and profit calculations
- **Monthly breakdown**: Performance over time

## 🔧 Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Database Migrations
```bash
cd backend
alembic upgrade head
```

## 🌐 Deployment

The application is configured for containerized deployment with:
- **Multi-stage Docker builds** for optimization
- **Environment-based configuration**
- **Health checks** and monitoring
- **Automated CI/CD** via GitHub Actions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Thai lottery data providers
- Vue.js and FastAPI communities
- Contributors and testers

---

**Built with ❤️ for Thai lottery enthusiasts**
