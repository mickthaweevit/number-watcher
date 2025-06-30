import httpx
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from ..database import get_db
from .data_processor import process_api_response
from ..models.game import Game
from ..models.result import Result

logger = logging.getLogger(__name__)

class ExternalAPIService:
    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.client = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def fetch_lottery_data(self, date: str) -> Optional[Dict[str, Any]]:
        """
        Fetch lottery data from external API for given date
        Args:
            date: Date string in format 'YYYY-MM-DDTHH:MM:SS.000Z'
        Returns:
            API response data or None if failed
        """
        if not self.base_url:
            logger.warning("No external API URL configured")
            return None
        
        try:
            url = f"{self.base_url}?dateCurrent={date}"
            logger.info(f"Fetching data from: {url}")
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            return response.json()
            
        except httpx.TimeoutException:
            logger.error(f"Timeout fetching data from external API")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} from external API")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching external API data: {str(e)}")
            return None
    
    async def import_live_data(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Import live lottery data and save to database
        Args:
            date: Optional date string, defaults to current date
        Returns:
            Import statistics
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')
        
        # Fetch data from external API
        api_data = await self.fetch_lottery_data(date)
        
        if not api_data:
            return {
                "success": False,
                "message": "Failed to fetch data from external API",
                "games_created": 0,
                "results_updated": 0,
                "total_records": 0
            }
        
        # Process and save data
        return await self._process_and_save_data(api_data)
    
    async def _process_and_save_data(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process API data and save to database"""
        try:
            # Process the API response
            processed_games = process_api_response(api_data)
            
            # Deduplicate by base_game_id + result_date
            unique_games = {}
            for game_data in processed_games:
                key = f"{game_data['base_game_id']}_{game_data['result_date']}"
                unique_games[key] = game_data
            
            processed_games = list(unique_games.values())
            
            # Save to database
            db = next(get_db())
            try:
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
                        db.flush()
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
                    "success": True,
                    "message": f"Successfully processed {imported_count} records from live API",
                    "games_created": games_created,
                    "results_updated": results_updated,
                    "total_records": len(processed_games)
                }
                
            except Exception as e:
                db.rollback()
                logger.error(f"Database error during live import: {str(e)}")
                return {
                    "success": False,
                    "message": f"Database error: {str(e)}",
                    "games_created": 0,
                    "results_updated": 0,
                    "total_records": 0
                }
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error processing live API data: {str(e)}")
            return {
                "success": False,
                "message": f"Processing error: {str(e)}",
                "games_created": 0,
                "results_updated": 0,
                "total_records": 0
            }

# Global service instance
external_api_service = ExternalAPIService()