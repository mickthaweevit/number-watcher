from fastapi import FastAPI, Depends, HTTPException, Query
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from .database import engine, get_db
from .models import game, result
from .models.game import Game
from .models.result import Result
from .schemas.game import Game as GameSchema
from .schemas.result import Result as ResultSchema
from .services.data_processor import process_api_response
from .services.external_api import ExternalAPIService
from .services.scheduler import lottery_scheduler
import json
import os
from datetime import datetime

# Create database tables
from .database import Base
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NumWatch API", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """Start the lottery data scheduler on app startup"""
    lottery_scheduler.start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the lottery data scheduler on app shutdown"""
    lottery_scheduler.stop_scheduler()

# CORS middleware for Vue 3 frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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

@app.get("/games", response_model=List[GameSchema])
async def get_games(db: Session = Depends(get_db)):
    """Get all games"""
    games = db.query(Game).all()
    return games

@app.get("/results", response_model=List[ResultSchema])
async def get_results(db: Session = Depends(get_db)):
    """Get all results with game information"""
    results = db.query(Result).join(Game).all()
    return results

@app.post("/import-sample-data")
async def import_sample_data(db: Session = Depends(get_db)):
    """Import data from responseData.json for testing"""
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
                    game_name=game_data['game_name'],
                    country_code=game_data['country_code'],
                    category=game_data['category']
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
        return {
            "message": f"Successfully processed {imported_count} records",
            "games_created": games_created,
            "results_updated": results_updated,
            "total_unique_records": len(processed_games)
        }
        
    except Exception as e:
        db.rollback()
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