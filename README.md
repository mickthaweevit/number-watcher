# 🎯 NumWatch - Thai Lottery Analysis System

A comprehensive Thai lottery number analysis and tracking system with real-time data import, advanced pattern analysis, and user management. Features per-game pattern betting with detailed financial calculations.

## 🌟 Key Features

### 🔐 Authentication & User Management
- **Secure JWT Authentication** with invite-based registration
- **Admin Panel** for user and invite code management
- **Multi-user Support** with individual profiles
- **Thai Language Interface** throughout the application

### 📊 Dual API Data Management
- **V1 & V2 API Support** with source selection
- **Real-time Data Import** from external lottery APIs
- **Automated Scheduler** for regular data updates
- **Data Export/Import** with source-aware backups
- **Buddhist Calendar Support** (พ.ศ. format)

### 🎲 Advanced Pattern Analysis
- **Dual Dashboard System**:
  - **NHLDashboard**: Per-game pattern betting (เบิ้ลหน้า, หาม, เบิ้ลหลัง)
  - **TargetNumber**: Digit-based analysis with OR/AND matching
- **Pattern Betting Features**:
  - Individual bet amounts per pattern per game
  - 90 numbers per pattern (เบิ้ลหน้า, หาม, เบิ้ลหลัง)
  - "ตัดเบิ้ล" (No Duplicate) filtering option
- **Real-time Financial Calculations**:
  - Win/Loss tracking per pattern
  - Net profit/loss calculations
  - Monthly breakdown by pattern
- **Visual Pattern Highlighting** in results table (display only)

### 📈 Comprehensive Analytics
- **Game-by-Game Analysis** with expandable monthly details
- **Pattern-specific Statistics** showing wins/losses per pattern
- **Aggregated Summary Statistics** across all games
- **Monthly Performance Tracking** with profit/loss trends
- **Bulk Game Management** with search filter and multi-select
- **Drag & Drop Game Reordering** via dedicated dialog

### 👤 Advanced Profile System
- **Per-Game Pattern Betting** profiles
- **Auto-save Detection** with unsaved changes protection
- **Profile Import/Export** with pattern bet preservation
- **Source-aware Profiles** (V1/V2 API compatibility)
- **Browser Navigation Guards** preventing data loss

### 🎮 Enhanced Game Management
- **Bulk Game Selection** via modal with table interface
- **Search Filter** for quick game discovery
- **Select All/None** functionality for efficient selection
- **Real-time Game Counter** showing selected games
- **Optimized Performance** with single bulk operation

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
- PostgreSQL database (local or cloud)
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
EXTERNAL_API_URL=https://api.lottery-v1.com
EXTERNAL_API_URL_V2=https://api.lottery-v2.com
CORS_ORIGINS=http://localhost:5173

# Frontend (.env)
VITE_API_URL=http://localhost:8000
```

3. **Run with Docker Compose**
```bash
docker-compose up -d
```

4. **Initialize database and admin**
```bash
# Create admin user
curl -X POST "http://localhost:8000/create-admin"

# Import sample data (optional)
curl -X POST "http://localhost:8000/import-sample-data-v2"
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
1. **Login** with your credentials or register with invite code
2. **Select API Source** (V1 or V2) for data import
3. **Add Games** to your analysis dashboard
4. **Choose Dashboard Type**:
   - **NHLDashboard**: Pattern-based betting (เบิ้ลหน้า, หาม, เบิ้ลหลัง)
   - **TargetNumber**: Digit-based analysis with OR/AND matching
5. **Configure Betting Strategy**:
   - **NHLDashboard**: Set individual bet amounts per pattern per game
   - **TargetNumber**: Select digits, match method, and global bet amount
   - **"ตัดเบิ้ล"**: Optional duplicate digit filtering
6. **Save Profile** to preserve your betting configuration

### Pattern Analysis System

#### NHLDashboard Patterns
- **เบิ้ลหน้า**: Numbers like 113, 225, 882 (first two digits same) - 90 possible numbers
- **หาม**: Numbers like 040, 747, 202 (first and last digits same) - 90 possible numbers
- **เบิ้ลหลัง**: Numbers like 200, 877, 399 (last two digits same) - 90 possible numbers
- **Prize Structure**: 1000x bet amount per winning number
- **Cost Structure**: 90 × bet amount per draw (covers all numbers in pattern)

#### TargetNumber Dashboard
- **OR Method**: Bet on numbers containing ANY selected digits
- **AND Method**: Bet on numbers containing ALL selected digits (max 3)
- **"ตัดเบิ้ล" Option**: Filter out numbers with duplicate digits
- **Dynamic Betting**: Cost varies based on method and digit selection
- **Examples**:
  - OR (digits 1,2): Bets on 001, 010, 012, 100, 102, 120, 121, 200, 201, 210, 212, etc.
  - AND (digits 1,2): Bets on 012, 021, 102, 120, 201, 210, etc.
  - With "ตัดเบิ้ล": Excludes 100, 011, 122, 211, etc.

### Reading Results
- **Pattern Highlighting**: Visual indicators for different patterns (display only)
- **Financial Calculations**: Real-time profit/loss per pattern per game
- **Statistics Table**: Individual game performance with expandable monthly details
- **Summary Statistics**: Aggregated performance across all active bets
- **Monthly Breakdown**: Pattern-specific performance trends

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

### Database Schema Updates
```bash
# For new columns (like game_pattern_bets)
docker-compose exec backend python add_migration_script.py

# Or manually via SQL
ALTER TABLE user_profiles ADD COLUMN game_pattern_bets JSON;
```

### API Source Management
```bash
# Switch between V1 and V2 APIs
localStorage.setItem('selectedApiSource', 'new') // V2
localStorage.setItem('selectedApiSource', 'old') // V1
```

## 🌐 Deployment

### Production Deployment
- **Docker Compose** for containerized deployment
- **PostgreSQL** database (Supabase recommended)
- **Environment-based configuration**
- **Health checks** and API monitoring
- **Source-aware data export/import** for backups

### Database Setup (Supabase)
1. Create new Supabase project
2. Run SQL migrations in Supabase SQL Editor
3. Update DATABASE_URL in environment variables
4. Deploy containers with updated configuration

### Environment Variables
```bash
# Production Backend
DATABASE_URL=postgresql://postgres:[password]@[host]:5432/postgres
EXTERNAL_API_URL=https://production-api-v1.com
EXTERNAL_API_URL_V2=https://production-api-v2.com
CORS_ORIGINS=https://your-domain.com

# Production Frontend  
VITE_API_URL=https://api.your-domain.com
```

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

## 📊 Data Structure

### Profile Schema

#### NHLDashboard Profile
```json
{
  "profile_name": "My NHL Strategy",
  "dashboard_type": "nhl_dashboard",
  "selected_patterns": ["first_two", "last_two"],
  "selected_game_ids": [1, 2, 3],
  "game_pattern_bets": {
    "1": {"first_two": 10, "first_third": 0, "last_two": 20},
    "2": {"first_two": 15, "first_third": 5, "last_two": 0}
  }
}
```

#### TargetNumber Profile
```json
{
  "profile_name": "My Target Strategy",
  "dashboard_type": "target_number",
  "game_pattern_bets": {
    "match_method": "OR",
    "target_digits": ["1", "2", "7"],
    "no_duplicate": true,
    "bet_amount": 10,
    "selected_games": [
      {"gameId": 1, "calculate": true},
      {"gameId": 2, "calculate": false}
    ]
  }
}
```

### Analysis Output
```json
{
  "month": "2025-01",
  "patternA": {"wins": 5, "losses": 25},
  "patternB": {"wins": 3, "losses": 27}, 
  "patternC": {"wins": 8, "losses": 22},
  "netAmount": 2500
}
```

---

**Built with ❤️ for Thai lottery enthusiasts**

*Advanced pattern analysis system with per-game betting strategies*
