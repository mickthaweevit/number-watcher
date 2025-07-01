from fastapi import FastAPI, Depends, HTTPException, Query
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from .database import engine, get_db
from .models import game, result, import_log, user, dashboard_profile, invite_code
from .models.game import Game
from .models.result import Result
from .models.import_log import ImportLog
from .models.user import User
from .models.dashboard_profile import DashboardProfile
from .models.invite_code import InviteCode
from .models.game_v2 import GameV2
from .models.result_v2 import ResultV2
from .schemas.game import Game as GameSchema
from .schemas.result import Result as ResultSchema
from .schemas.import_log import ImportLog as ImportLogSchema
from .schemas.user import UserCreate, UserLogin, UserResponse, Token
from .schemas.dashboard_profile import DashboardProfileCreate, DashboardProfileResponse
from .schemas.invite_code import InviteCodeCreate, InviteCodeResponse, UserRegisterWithInvite
from .services.auth import authenticate_user, create_access_token, get_current_user, get_password_hash
from .services.data_processor import process_api_response
from .services.data_processor_v2 import process_api_response_v2
from .services.external_api import ExternalAPIService
from .services.external_api_v2 import ExternalAPIServiceV2
from .services.scheduler import lottery_scheduler
import json
import os
from datetime import datetime

# Create database tables
from .database import Base
# Import all models to ensure they're registered
from .models import game, result, import_log, user, dashboard_profile, invite_code, game_v2, result_v2
# Create database tables (with error handling for deployment)
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
except Exception as e:
    print(f"⚠️ Database connection failed during startup: {e}")
    print("📝 Tables will be created on first API call")
    # Don't fail the app startup - let it handle DB connection later

app = FastAPI(title="NumWatch API", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """Start the lottery data scheduler on app startup"""
    lottery_scheduler.start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the lottery data scheduler on app shutdown"""
    lottery_scheduler.stop_scheduler()

# CORS middleware - support both development and production
import os

# Get CORS origins from environment or use default
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "NumWatch API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/performance")
async def check_performance(db: Session = Depends(get_db)):
    """Check database performance metrics"""
    import time
    from sqlalchemy import text
    
    metrics = {}
    
    # Test results query performance
    start = time.time()
    result_count = db.query(Result).count()
    metrics["results_count_time"] = round((time.time() - start) * 1000, 2)
    metrics["total_results"] = result_count
    
    # Test games query performance
    start = time.time()
    game_count = db.query(Game).count()
    metrics["games_count_time"] = round((time.time() - start) * 1000, 2)
    metrics["total_games"] = game_count
    
    # Test join query performance
    start = time.time()
    join_count = db.query(Result).join(Game).count()
    metrics["join_query_time"] = round((time.time() - start) * 1000, 2)
    
    # Check if indexes exist
    try:
        index_check = db.execute(text("""
            SELECT COUNT(*) as index_count 
            FROM pg_indexes 
            WHERE tablename IN ('results', 'games') 
            AND indexname LIKE 'idx_%'
        """)).fetchone()
        metrics["custom_indexes"] = index_check[0] if index_check else 0
    except:
        metrics["custom_indexes"] = "error"
    
    return metrics

@app.get("/db-test")
async def test_database():
    """Test database connection"""
    try:
        # Try to connect to database
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return {"database": "connected", "test_query": "success"}
    except Exception as e:
        return {"database": "failed", "error": str(e)}

@app.get("/db-info")
async def get_database_info():
    """Show database connection info (without password)"""
    import os
    from urllib.parse import urlparse
    
    db_url = os.getenv("DATABASE_URL", "Not set")
    
    if db_url == "Not set":
        return {"error": "DATABASE_URL environment variable not set"}
    
    try:
        parsed = urlparse(db_url)
        return {
            "host": parsed.hostname,
            "port": parsed.port,
            "database": parsed.path.lstrip('/'),
            "username": parsed.username,
            "password_set": "Yes" if parsed.password else "No",
            "password_length": len(parsed.password) if parsed.password else 0,
            "full_url_set": "Yes"
        }
    except Exception as e:
        return {"error": f"Failed to parse DATABASE_URL: {str(e)}"}

@app.get("/games", response_model=List[GameSchema])
async def get_games(
    source: str = Query("old", description="API source: old or new"),
    db: Session = Depends(get_db)
):
    """Get games with source selection"""
    try:
        if source == "new":
            # Query new tables and map to old format
            try:
                games_v2 = db.query(GameV2).filter(GameV2.is_active == True).all()
                
                # Map to old format
                mapped_games = []
                for g in games_v2:
                    game_obj = Game(
                        id=g.id,
                        game_name=g.product_name_th,
                        base_game_id=str(g.product_id),
                        is_active=g.is_active,
                        created_at=g.created_at,
                        updated_at=g.created_at
                    )
                    mapped_games.append(game_obj)
                return mapped_games
            except Exception as e:
                print(f"Error querying new games: {str(e)}")
                # Return empty list if tables don't exist or are empty
                return []
        else:
            # Original old format query
            games = db.query(Game).filter(Game.is_active == True).all()
            return games
    except Exception as e:
        print(f"Error in get_games: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/results", response_model=List[ResultSchema])
async def get_results(
    source: str = Query("old", description="API source: old or new"),
    db: Session = Depends(get_db)
):
    """Get results with source selection"""
    try:
        if source == "new":
            # Query new tables and map to old format
            try:
                results_v2 = db.query(ResultV2).join(GameV2).all()
                
                # Map to old format
                mapped_results = []
                for r in results_v2:
                    result_obj = Result(
                        id=r.id,
                        game_id=r.game_id,
                        full_game_code=f"V2-{r.period_id}",  # Generate a code
                        result_date=r.result_date,
                        result_3up=r.award1,
                        result_2down=r.award2,
                        result_4up=r.award3,
                        status=r.status,
                        created_at=r.created_at,
                        updated_at=r.created_at
                    )
                    result_obj.game = Game(
                        id=r.game.id,
                        game_name=r.game.product_name_th,
                        base_game_id=str(r.game.product_id),
                        is_active=r.game.is_active,
                        created_at=r.game.created_at,
                        updated_at=r.game.created_at
                    )
                    mapped_results.append(result_obj)
                return mapped_results
            except Exception as e:
                print(f"Error querying new tables: {str(e)}")
                # Return empty list if tables don't exist or are empty
                return []
        else:
            # Original old format query
            from sqlalchemy.orm import joinedload
            results = db.query(Result).options(joinedload(Result.game)).all()
            return results
    except Exception as e:
        print(f"Error in get_results (optimized): {str(e)}")
        # Fallback to original query
        try:
            results = db.query(Result).join(Game).all()
            return results
        except Exception as fallback_error:
            print(f"Fallback error: {str(fallback_error)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/import-sample-data")
async def import_sample_data(db: Session = Depends(get_db)):
    """Import data from responseData.json for testing"""
    # Create import log entry
    import_log = ImportLog(
        filename="responseData.json",
        import_type="sample_data",
        status="running"
    )
    db.add(import_log)
    db.flush()
    
    try:
        # Read the sample data file
        with open('/app/responseData.json', 'r', encoding='utf-8') as file:
            api_data = json.load(file)
        
        # Process the API response
        processed_games = process_api_response(api_data)
        
        # Deduplicate by base_game_id + result_date
        unique_games = {}
        for game_data in processed_games:
            key = f"{game_data['base_game_id']}_{game_data['result_date']}"
            unique_games[key] = game_data
        
        processed_games = list(unique_games.values())
        
        imported_count = 0
        games_created = 0
        results_updated = 0
        
        for game_data in processed_games:
            # Check if game exists, if not create it
            game = db.query(Game).filter(Game.base_game_id == game_data['base_game_id']).first()
            if not game:
                game = Game(
                    base_game_id=game_data['base_game_id'],
                    game_name=game_data['game_name']
                )
                db.add(game)
                db.flush()  # Flush to get the ID without committing
                games_created += 1
            
            # Check if result exists for this game and date
            existing_result = db.query(Result).filter(
                Result.game_id == game.id,
                Result.result_date == game_data['result_date']
            ).first()
            
            if existing_result:
                # Update existing result
                existing_result.result_3up = game_data['result_3up']
                existing_result.result_2down = game_data['result_2down']
                existing_result.result_4up = game_data['result_4up']
                existing_result.status = game_data['status']
                existing_result.full_game_code = game_data['full_game_code']
                results_updated += 1
            else:
                # Create new result
                new_result = Result(
                    game_id=game.id,
                    full_game_code=game_data['full_game_code'],
                    result_date=game_data['result_date'],
                    result_3up=game_data['result_3up'],
                    result_2down=game_data['result_2down'],
                    result_4up=game_data['result_4up'],
                    status=game_data['status']
                )
                db.add(new_result)
            
            imported_count += 1
        
        db.commit()
        
        # Update import log with success
        import_log.status = "success"
        import_log.completed_at = datetime.now()
        import_log.records_processed = imported_count
        import_log.games_created = games_created
        import_log.results_created = results_updated
        db.commit()
        
        return {
            "message": f"Successfully processed {imported_count} records",
            "games_created": games_created,
            "results_updated": results_updated,
            "total_unique_records": len(processed_games)
        }
        
    except Exception as e:
        db.rollback()
        
        # Update import log with failure
        import_log.status = "failed"
        import_log.completed_at = datetime.now()
        import_log.error_message = str(e)
        db.commit()
        
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

@app.post("/import-live-data")
async def import_live_data(date: Optional[str] = Query(None, description="Date in format YYYY-MM-DDTHH:MM:SS.000Z, defaults to today")):
    # Set default date to today if not provided
    if date is None:
        date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')
    external_api_url = os.getenv("EXTERNAL_API_URL")
    
    if not external_api_url:
        raise HTTPException(
            status_code=400, 
            detail="External API URL not configured. Set EXTERNAL_API_URL environment variable."
        )
    
    try:
        async with ExternalAPIService(base_url=external_api_url) as api_service:
            result = await api_service.import_live_data(date)
            
            if not result["success"]:
                raise HTTPException(status_code=500, detail=result["message"])
            
            return result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Live import failed: {str(e)}")

@app.get("/scheduler/status")
async def get_scheduler_status():
    """Get scheduler status and next scheduled jobs"""
    return lottery_scheduler.get_status()

@app.post("/scheduler/start")
async def start_scheduler():
    """Start the lottery data scheduler"""
    lottery_scheduler.start_scheduler()
    return {"message": "Scheduler started", "status": lottery_scheduler.get_status()}

@app.post("/scheduler/stop")
async def stop_scheduler():
    """Stop the lottery data scheduler"""
    lottery_scheduler.stop_scheduler()
    return {"message": "Scheduler stopped", "status": lottery_scheduler.get_status()}

@app.post("/scheduler/trigger")
async def trigger_manual_import():
    """Manually trigger a scheduled import"""
    result = lottery_scheduler.trigger_manual_import()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@app.post("/scheduler/import-range")
async def import_date_range(
    start_date: str = Query(..., description="Start date in format YYYY-MM-DDTHH:MM:SS.000Z"),
    end_date: str = Query(..., description="End date in format YYYY-MM-DDTHH:MM:SS.000Z")
):
    """Import data for a date range (max 30 days)"""
    result = lottery_scheduler.trigger_date_range_import(start_date, end_date)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result



@app.get("/import-logs", response_model=List[ImportLogSchema])
async def get_import_logs(db: Session = Depends(get_db)):
    """Get recent import logs (last 20)"""
    logs = db.query(ImportLog).order_by(ImportLog.started_at.desc()).limit(20).all()
    return logs

@app.delete("/import-logs")
async def clear_import_logs(db: Session = Depends(get_db)):
    """Clear all import log histories"""
    try:
        logs_deleted = db.query(ImportLog).count()
        db.query(ImportLog).delete()
        db.commit()
        
        return {
            "message": "Import logs cleared successfully",
            "logs_deleted": logs_deleted
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Clear logs failed: {str(e)}")

@app.get("/export-data")
async def export_data(db: Session = Depends(get_db)):
    """Export all data as JSON backup"""
    try:
        # Get all games with their results
        games = db.query(Game).all()
        results = db.query(Result).all()
        
        # Convert to dictionaries
        games_data = []
        for game in games:
            games_data.append({
                "id": game.id,
                "base_game_id": game.base_game_id,
                "game_name": game.game_name,
                "is_active": game.is_active,
                "created_at": game.created_at.isoformat() if game.created_at else None
            })
        
        results_data = []
        for result in results:
            results_data.append({
                "id": result.id,
                "game_id": result.game_id,
                "full_game_code": result.full_game_code,
                "result_date": result.result_date.isoformat() if result.result_date else None,
                "result_3up": result.result_3up,
                "result_2down": result.result_2down,
                "result_4up": result.result_4up,
                "status": result.status,
                "created_at": result.created_at.isoformat() if result.created_at else None
            })
        
        backup_data = {
            "export_date": datetime.now().isoformat(),
            "version": "1.0",
            "games": games_data,
            "results": results_data,
            "stats": {
                "total_games": len(games_data),
                "total_results": len(results_data)
            }
        }
        
        return backup_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.post("/import-backup")
async def import_backup(backup_data: dict, db: Session = Depends(get_db)):
    """Import data from JSON backup"""
    # Extract metadata if provided
    metadata = backup_data.get("_metadata", {})
    filename = metadata.get("filename")
    file_size = metadata.get("file_size")
    
    # Create import log entry
    import_log = ImportLog(
        filename=filename,
        import_type="backup",
        status="running",
        records_processed=len(backup_data.get("games", [])) + len(backup_data.get("results", [])),
        file_size=file_size
    )
    db.add(import_log)
    db.flush()
    
    try:
        if "games" not in backup_data or "results" not in backup_data:
            raise HTTPException(status_code=400, detail="Invalid backup format")
        
        games_created = 0
        results_created = 0
        
        # Import games first
        for game_data in backup_data["games"]:
            existing_game = db.query(Game).filter(Game.base_game_id == game_data["base_game_id"]).first()
            if not existing_game:
                new_game = Game(
                    base_game_id=game_data["base_game_id"],
                    game_name=game_data["game_name"],
                    is_active=game_data.get("is_active", True)
                )
                db.add(new_game)
                games_created += 1
        
        db.flush()  # Flush to get game IDs
        
        # Import results
        for result_data in backup_data["results"]:
            # Find the game by base_game_id (since IDs might be different)
            game = db.query(Game).filter(Game.base_game_id.in_(
                [g["base_game_id"] for g in backup_data["games"] if g["id"] == result_data["game_id"]]
            )).first()
            
            if game:
                existing_result = db.query(Result).filter(
                    Result.game_id == game.id,
                    Result.result_date == result_data["result_date"]
                ).first()
                
                if not existing_result:
                    new_result = Result(
                        game_id=game.id,
                        full_game_code=result_data["full_game_code"],
                        result_date=result_data["result_date"],
                        result_3up=result_data["result_3up"],
                        result_2down=result_data["result_2down"],
                        result_4up=result_data["result_4up"],
                        status=result_data["status"]
                    )
                    db.add(new_result)
                    results_created += 1
        
        db.commit()
        
        # Update import log with success
        import_log.status = "success"
        import_log.completed_at = datetime.now()
        import_log.games_created = games_created
        import_log.results_created = results_created
        db.commit()
        
        return {
            "message": "Backup imported successfully",
            "games_created": games_created,
            "results_created": results_created
        }
        
    except Exception as e:
        db.rollback()
        
        # Update import log with failure
        import_log.status = "failed"
        import_log.completed_at = datetime.now()
        import_log.error_message = str(e)
        db.commit()
        
        raise HTTPException(status_code=500, detail=f"Import backup failed: {str(e)}")

@app.delete("/clear-data")
async def clear_data(db: Session = Depends(get_db)):
    """Clear all data for testing purposes"""
    try:
        results_deleted = db.query(Result).count()
        games_deleted = db.query(Game).count()
        
        db.query(Result).delete()
        db.query(Game).delete()
        db.commit()
        
        return {
            "message": "All data cleared successfully",
            "results_deleted": results_deleted,
            "games_deleted": games_deleted
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Clear failed: {str(e)}")

# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserRegisterWithInvite, db: Session = Depends(get_db)):
    """Register a new user with invite code"""
    # Validate invite code
    invite = db.query(InviteCode).filter(
        InviteCode.code == user_data.invite_code,
        InviteCode.is_used == False
    ).first()
    
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid or used invite code")
    
    # Check if invite code is expired
    if invite.expires_at and invite.expires_at < datetime.now():
        raise HTTPException(status_code=400, detail="Invite code has expired")
    
    # Check if username already exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.flush()
    
    # Mark invite code as used
    invite.is_used = True
    invite.used_by = db_user.id
    
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = datetime.now()
    db.commit()
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

# Profile endpoints
@app.get("/profiles", response_model=List[DashboardProfileResponse])
async def get_user_profiles(
    source: str = Query("old", description="API source: old or new"),
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Get dashboard profiles for current user filtered by API source"""
    profiles = db.query(DashboardProfile).filter(
        DashboardProfile.user_id == current_user.id,
        DashboardProfile.api_source == source
    ).all()
    return profiles

@app.post("/profiles", response_model=DashboardProfileResponse)
async def create_profile(profile_data: DashboardProfileCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create a new dashboard profile for current user"""
    # Check if profile name already exists for this user and source
    existing_profile = db.query(DashboardProfile).filter(
        DashboardProfile.user_id == current_user.id,
        DashboardProfile.profile_name == profile_data.profile_name,
        DashboardProfile.api_source == profile_data.api_source
    ).first()
    
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile name already exists for this API source")
    
    db_profile = DashboardProfile(
        user_id=current_user.id,
        profile_name=profile_data.profile_name,
        bet_amount=profile_data.bet_amount,
        selected_patterns=profile_data.selected_patterns,
        selected_game_ids=profile_data.selected_game_ids,
        api_source=profile_data.api_source
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    return db_profile

@app.put("/profiles/{profile_id}", response_model=DashboardProfileResponse)
async def update_profile(profile_id: int, profile_data: DashboardProfileCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update a dashboard profile (only if it belongs to current user)"""
    profile = db.query(DashboardProfile).filter(
        DashboardProfile.id == profile_id,
        DashboardProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Update profile fields
    profile.profile_name = profile_data.profile_name
    profile.bet_amount = profile_data.bet_amount
    profile.selected_patterns = profile_data.selected_patterns
    profile.selected_game_ids = profile_data.selected_game_ids
    profile.api_source = profile_data.api_source
    profile.updated_at = datetime.now()
    
    db.commit()
    db.refresh(profile)
    
    return profile

@app.delete("/profiles/{profile_id}")
async def delete_profile(profile_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a dashboard profile (only if it belongs to current user)"""
    profile = db.query(DashboardProfile).filter(
        DashboardProfile.id == profile_id,
        DashboardProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db.delete(profile)
    db.commit()
    
    return {"message": "Dashboard profile deleted successfully"}

# Admin-only endpoints
def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@app.post("/admin/invite-codes", response_model=InviteCodeResponse)
async def create_invite_code(invite_data: InviteCodeCreate, admin_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Create a new invite code (admin only)"""
    import secrets
    
    code = secrets.token_urlsafe(16)
    
    db_invite = InviteCode(
        code=code,
        created_by=admin_user.id,
        expires_at=invite_data.expires_at
    )
    db.add(db_invite)
    db.commit()
    db.refresh(db_invite)
    
    return db_invite

@app.get("/admin/invite-codes", response_model=List[InviteCodeResponse])
async def get_invite_codes(admin_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Get all invite codes (admin only)"""
    codes = db.query(InviteCode).order_by(InviteCode.created_at.desc()).all()
    return codes

@app.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(admin_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Get all users (admin only)"""
    users = db.query(User).order_by(User.created_at.desc()).all()
    return users

@app.post("/import-sample-data-v2")
async def import_sample_data_v2(db: Session = Depends(get_db)):
    """Import data from responseDataNew.json for testing new format"""
    # Create import log entry
    import_log = ImportLog(
        filename="responseDataNew.json",
        import_type="sample_data_v2",
        status="running"
    )
    db.add(import_log)
    db.flush()
    
    try:
        # Read the new sample data file
        import os
        # Try different paths for local vs production
        possible_paths = [
            '/app/responseDataNew.json',  # Production path
            'responseDataNew.json',       # Local relative path
            '../responseDataNew.json'     # Local parent directory
        ]
        
        api_data = None
        for path in possible_paths:
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    api_data = json.load(file)
                    break
            except FileNotFoundError:
                continue
        
        if api_data is None:
            raise FileNotFoundError("responseDataNew.json not found in any expected location")
        
        # Process the API response with new processor (use today's date)
        today_date = datetime.now().strftime('%Y%m%d')
        processed_games = process_api_response_v2(api_data, today_date)
        
        # Deduplicate by product_id + result_date + yk_round
        unique_games = {}
        for game_data in processed_games:
            key = f"{game_data['product_id']}_{game_data['result_date']}_{game_data['yk_round']}"
            unique_games[key] = game_data
        
        processed_games = list(unique_games.values())
        
        imported_count = 0
        games_created = 0
        results_created = 0
        
        print(f"Processing {len(processed_games)} games from v2 format")
        
        for game_data in processed_games:
            print(f"Processing game: {game_data['product_name_th']} (ID: {game_data['product_id']})")
            
            # Check if game exists, if not create it
            game = db.query(GameV2).filter(GameV2.product_id == game_data['product_id']).first()
            if not game:
                print(f"Creating new game: {game_data['product_name_th']}")
                game = GameV2(
                    product_id=game_data['product_id'],
                    product_name_th=game_data['product_name_th'],
                    product_code=game_data['product_code']
                )
                db.add(game)
                db.flush()
                games_created += 1
            else:
                print(f"Game already exists: {game_data['product_name_th']}")
            
            # Check if result exists for this game, date and round
            existing_result = db.query(ResultV2).filter(
                ResultV2.game_id == game.id,
                ResultV2.result_date == game_data['result_date'],
                ResultV2.yk_round == game_data['yk_round']
            ).first()
            
            if not existing_result:
                print(f"Creating new result for game {game.id}, date {game_data['result_date']}")
                new_result = ResultV2(
                    game_id=game.id,
                    period_id=game_data['period_id'],
                    award1=game_data['award1'],
                    award2=game_data['award2'],
                    award3=game_data['award3'],
                    result_date=game_data['result_date'],
                    status=game_data['status'],
                    yk_round=game_data['yk_round']
                )
                db.add(new_result)
                results_created += 1
            else:
                print(f"Result already exists for game {game.id}, date {game_data['result_date']}")
            
            imported_count += 1
        
        db.commit()
        
        # Update import log with success
        import_log.status = "success"
        import_log.completed_at = datetime.now()
        import_log.records_processed = imported_count
        import_log.games_created = games_created
        import_log.results_created = results_created
        db.commit()
        
        return {
            "message": f"Successfully processed {imported_count} records from new format",
            "games_created": games_created,
            "results_created": results_created,
            "total_unique_records": len(processed_games),
            "filtered_products": len([item for item in api_data.get('info', []) if item.get('productCode') not in ['YK', 'YK5', 'TH']])
        }
        
    except Exception as e:
        db.rollback()
        
        # Update import log with failure
        import_log.status = "failed"
        import_log.completed_at = datetime.now()
        import_log.error_message = str(e)
        db.commit()
        
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

@app.post("/import-live-data-v2")
async def import_live_data_v2(
    date: Optional[str] = Query(None, description="Date in format YYYYMMDD, defaults to today"),
    db: Session = Depends(get_db)
):
    """Import live data from new API format"""
    # Set default date to today if not provided
    if date is None:
        date = datetime.now().strftime('%Y%m%d')
    
    external_api_url_v2 = os.getenv("EXTERNAL_API_URL_V2")
    
    if not external_api_url_v2:
        raise HTTPException(
            status_code=400, 
            detail="External API URL V2 not configured. Set EXTERNAL_API_URL_V2 environment variable."
        )
    
    try:
        async with ExternalAPIServiceV2(base_url=external_api_url_v2) as api_service:
            result = await api_service.import_data_for_date(date, db)
            
            if not result["success"]:
                raise HTTPException(status_code=500, detail=result["message"])
            
            return result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Live import failed: {str(e)}")

@app.post("/import-date-range-v2")
async def import_date_range_v2(
    start_date: str = Query(..., description="Start date in format YYYYMMDD"),
    end_date: str = Query(..., description="End date in format YYYYMMDD"),
    db: Session = Depends(get_db)
):
    """Import data for a date range from new API format"""
    external_api_url_v2 = os.getenv("EXTERNAL_API_URL_V2")
    
    if not external_api_url_v2:
        raise HTTPException(
            status_code=400, 
            detail="External API URL V2 not configured. Set EXTERNAL_API_URL_V2 environment variable."
        )
    
    try:
        async with ExternalAPIServiceV2(base_url=external_api_url_v2) as api_service:
            result = await api_service.import_date_range(start_date, end_date, db)
            
            return result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Date range import failed: {str(e)}")

@app.post("/create-admin")
async def create_admin_user(db: Session = Depends(get_db)):
    """Create first admin user - only works if no admin exists"""
    try:
        # Ensure database tables exist
        Base.metadata.create_all(bind=engine)
        
        # Check if any admin already exists
        existing_admin = db.query(User).filter(User.is_admin == True).first()
        if existing_admin:
            raise HTTPException(status_code=400, detail="Admin user already exists")
        
        # Generate secure password
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        admin_password = ''.join(secrets.choice(alphabet) for _ in range(12))
        
        # Create admin user
        hashed_password = get_password_hash(admin_password)
        admin_user = User(
            username="admin",
            email="admin@numwatch.app",
            password_hash=hashed_password,
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        return {
            "message": "Admin user created successfully",
            "username": "admin",
            "password": admin_password,
            "email": "admin@numwatch.app",
            "warning": "Save these credentials! Password will not be shown again."
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create admin: {str(e)}")