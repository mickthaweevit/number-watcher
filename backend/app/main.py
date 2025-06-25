from fastapi import FastAPI, Depends, HTTPException
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
import json

# Create database tables
from .database import Base
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NumWatch API", version="1.0.0")

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