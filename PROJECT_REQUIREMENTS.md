# Lottery Result Tracker - Project Requirements

## Project Overview
Full-stack lottery result tracking system to store and display lottery results from multiple countries and game types in a table format with Date (X-axis) vs Game Name (Y-axis).

## Tech Stack Decision
**Selected**: Option B - Python + FastAPI + React
- **Backend**: Python + FastAPI + PostgreSQL
- **Frontend**: React + TypeScript
- **Development Environment**: Full Docker setup (Option A)
- **Benefits**: Python excellent for data processing, FastAPI modern and fast, great for learning

## Data Source
- **Source**: External API (no documentation available)
- **Sample Data**: responseData.json (contains actual API response structure)
- **API Query**: `?dateCurrent=2025-06-21T17%3A00%3A00.000Z`
- **API URL**: To be provided later

## Data Structure Analysis

### API Response Categories
- `set` - Basic lottery games
- `settrade` - VIP games  
- `settradeInt` - International META games
- `settrandNoInt` - Non-international games
- `settradeVIP`, `settradeVISA`, `settradeVI`, `settradeHIT` - Various VIP categories
- `newSettrade` - New settlement games

### GAME_CODE Pattern
- **Format**: `L03-01-000500-20250622`
- **Structure**: `[BASE_GAME_ID]-[DATE]`
- **Example**: 
  - Full Code: `L03-01-000500-20250622`
  - Base Game ID: `L03-01-000500`
  - Date: `20250622` → `2025-06-22`

### Result Types
- **Normal Results**: Numeric values (e.g., "123", "45")
- **Waiting Status**: "รอผล" (waiting for result)
- **Cancelled Status**: "ยกเลิก" (cancelled)
- **Missing Results**: Some games don't have results every day

## Database Design

### Games Table (Master Data)
```sql
games (
  id SERIAL PRIMARY KEY,
  base_game_id VARCHAR(50) UNIQUE,    -- "L03-01-000500"
  game_name VARCHAR(200),             -- "ดาวโจนส์ VIP"
  country_code VARCHAR(10),           -- "US", "LA", "VN", etc.
  category VARCHAR(50),               -- "settrade", "settradeInt", "set"
  is_active BOOLEAN DEFAULT true,     -- for hiding/showing games
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

### Results Table (Daily Data)
```sql
results (
  id SERIAL PRIMARY KEY,
  game_id INTEGER REFERENCES games(id),
  full_game_code VARCHAR(100),        -- "L03-01-000500-20250622"
  result_date DATE,                   -- "2025-06-22"
  result_3up VARCHAR(10),             -- 3-digit result
  result_2down VARCHAR(10),           -- 2-digit result
  result_4up VARCHAR(10),             -- 4-digit result
  status VARCHAR(20) DEFAULT 'completed', -- 'waiting', 'cancelled', 'completed', 'no_result'
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  UNIQUE(game_id, result_date)        -- prevent duplicate results
)
```

## Result Status Logic

### Status Types
- `waiting` → "รอผล" (waiting for result)
- `cancelled` → "ยกเลิก" (cancelled)  
- `completed` → Normal numbers like "123", "45"
- `no_result` → Not in API response (missing)

### Processing Logic
```python
def process_api_result(result_value):
    if result_value == "รอผล":
        return "waiting", result_value
    elif result_value == "ยกเลิก":
        return "cancelled", result_value
    elif result_value and result_value.replace('-', '').isdigit():
        return "completed", result_value
    else:
        return "no_result", None
```

## Data Import Strategy

### Automated Import
- **Frequency**: Every hour (configurable)
- **Process**: 
  1. Call external API with current date
  2. Parse response data
  3. Auto-add new games to database
  4. Update existing results with new status
  5. Handle missing results appropriately

### Status Updates
- **No History Needed**: Only store current status
- **Update Flow**: "รอผล" → actual numbers or "ยกเลิก"

## Frontend Requirements

### Table Display
- **X-axis**: Dates (columns)
- **Y-axis**: Game Names (rows)
- **Cell Content**: Results or status indicators

### Display Examples
```
Date1      Date2        Date3
Game A     "123/45"     "รอผล"       "ยกเลิก"
Game B     "789/12"     "-"          "456/78"
Game C     "-"          "345/67"     "รอผล"
```

### Features Required
- **Category Filtering**: Filter by settrade, settradeInt, etc.
- **Country Filtering**: Filter by country codes
- **Date Range Selection**: Select date range for display
- **Missing Data Handling**: Show "-" or "N/A" for missing results
- **Status Indicators**: Clear display of waiting/cancelled status

## Project Structure
```
lottery-tracker/
├── backend/
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── scheduler/      # API import scheduler
│   │   └── main.py         # FastAPI app
│   ├── requirements.txt
│   ├── Dockerfile
│   └── database.py
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Main pages
│   │   ├── services/       # API calls
│   │   └── types/          # TypeScript types
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml      # Full Docker setup
├── PROJECT_REQUIREMENTS.md
└── README.md
```

## Development Phases

### Phase 1: Backend Foundation
- Database setup with models
- Basic API endpoints for CRUD operations
- Data import from JSON sample

### Phase 2: API Integration
- External API integration
- Scheduled data import (hourly)
- Status management system

### Phase 3: Frontend Development
- React table component
- Date vs Game Name layout
- Basic filtering and search

### Phase 4: Advanced Features
- Real-time status updates
- Advanced filtering options
- Data visualization
- Export functionality

## Learning Objectives
- **Backend Skills**: REST APIs, database design, data validation, scheduling
- **Frontend Skills**: React, state management, table components, TypeScript
- **Database Skills**: SQL queries, relationships, data normalization
- **Integration**: API consumption, data transformation, error handling
- **DevOps**: Environment management, deployment basics

## Technical Decisions Made

### Database & Infrastructure
1. ✅ **Database**: PostgreSQL (better for learning real-world skills)
2. ✅ **Development Environment**: Full Docker setup (Option A)
3. ✅ **Docker Architecture**: Backend + Frontend + PostgreSQL in containers
4. ✅ **Authentication**: Add later with third-party (Google/GitHub)

### Data Management
5. ✅ Store both full GAME_CODE and base game ID
6. ✅ Include category field for filtering
7. ✅ Handle missing results with status system
8. ✅ Auto-add new games from API responses
9. ✅ **Data Retention**: Keep forever
10. ✅ **Duplicate Handling**: Replace existing results
11. ✅ **Timezone**: Display in local timezone

### Development Approach
12. ✅ **Scheduling**: Hourly API calls (configurable)
13. ✅ **Status History**: Current status only (no history)
14. ✅ **Game Visibility**: Use is_active field for control
15. ✅ **Code Style**: Moderate comments (good but not excessive)
16. ✅ **Complexity**: Start simple, add advanced features incrementally

## Development Priority & Next Steps

### **Priority #1**: External API → Database Storage
First working feature should be getting data from external API and storing in database.

### Development Phases
1. **Phase 1**: Docker + PostgreSQL + FastAPI setup
2. **Phase 2**: External API integration + data storage  
3. **Phase 3**: Basic table display
4. **Phase 4**: Add advanced features incrementally

### Immediate Next Steps
1. Create Docker setup (docker-compose.yml)
2. Set up FastAPI backend with PostgreSQL
3. Implement database models
4. Create external API integration
5. Test data import and storage
6. Set up React frontend foundation

### Docker Services Architecture
```yaml
# docker-compose.yml structure
services:
  postgres:     # PostgreSQL database
  backend:      # FastAPI application
  frontend:     # React development server
```

### Access Points
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000  
- Database: localhost:5432