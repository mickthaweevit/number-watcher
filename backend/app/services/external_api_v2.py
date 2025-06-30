import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.game_v2 import GameV2
from ..models.result_v2 import ResultV2
from ..models.import_log import ImportLog
from .data_processor_v2 import process_api_response_v2

class ExternalAPIServiceV2:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_data_for_date(self, date_str: str) -> Dict[str, Any]:
        """
        Fetch data for a specific date
        date_str format: YYYYMMDD (e.g., "20250625")
        """
        url = f"{self.base_url}/info/getResult/{date_str}"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    print(f"API returned status {response.status} for date {date_str}")
                    return {"success": False, "info": []}
        except Exception as e:
            print(f"Error fetching data for {date_str}: {str(e)}")
            return {"success": False, "info": []}
    
    async def import_data_for_date(self, date_str: str, db: Session) -> Dict[str, Any]:
        """Import data for a specific date"""
        
        # Create import log
        import_log = ImportLog(
            filename=f"api_v2_{date_str}",
            import_type="live_data_v2",
            status="running"
        )
        db.add(import_log)
        db.flush()
        
        try:
            # Fetch data from API
            api_data = await self.fetch_data_for_date(date_str)
            
            if not api_data.get("success"):
                raise Exception(f"API returned unsuccessful response for {date_str}")
            
            # Process the data using periodName dates
            processed_games = process_api_response_v2(api_data)
            
            if not processed_games:
                import_log.status = "success"
                import_log.completed_at = datetime.now()
                import_log.records_processed = 0
                db.commit()
                return {
                    "success": True,
                    "message": f"No valid data found for {date_str}",
                    "games_created": 0,
                    "results_created": 0
                }
            
            # Import to database
            games_created = 0
            results_created = 0
            
            for game_data in processed_games:
                # Check if game exists
                game = db.query(GameV2).filter(GameV2.product_id == game_data['product_id']).first()
                if not game:
                    game = GameV2(
                        product_id=game_data['product_id'],
                        product_name_th=game_data['product_name_th'],
                        product_code=game_data['product_code']
                    )
                    db.add(game)
                    db.flush()
                    games_created += 1
                
                # Check if result exists
                existing_result = db.query(ResultV2).filter(
                    ResultV2.game_id == game.id,
                    ResultV2.result_date == game_data['result_date'],
                    ResultV2.yk_round == game_data['yk_round']
                ).first()
                
                if not existing_result:
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
            
            db.commit()
            
            # Update import log
            import_log.status = "success"
            import_log.completed_at = datetime.now()
            import_log.records_processed = len(processed_games)
            import_log.games_created = games_created
            import_log.results_created = results_created
            db.commit()
            
            return {
                "success": True,
                "message": f"Successfully imported data for {date_str}",
                "games_created": games_created,
                "results_created": results_created,
                "total_records": len(processed_games)
            }
            
        except Exception as e:
            db.rollback()
            import_log.status = "failed"
            import_log.completed_at = datetime.now()
            import_log.error_message = str(e)
            db.commit()
            
            return {
                "success": False,
                "message": f"Import failed for {date_str}: {str(e)}"
            }
    
    async def import_date_range(self, start_date: str, end_date: str, db: Session) -> Dict[str, Any]:
        """Import data for a date range"""
        
        try:
            start_dt = datetime.strptime(start_date, '%Y%m%d')
            end_dt = datetime.strptime(end_date, '%Y%m%d')
        except ValueError:
            return {
                "success": False,
                "message": "Invalid date format. Use YYYYMMDD"
            }
        
        if (end_dt - start_dt).days > 30:
            return {
                "success": False,
                "message": "Date range cannot exceed 30 days"
            }
        
        results = []
        current_date = start_dt
        
        while current_date <= end_dt:
            date_str = current_date.strftime('%Y%m%d')
            result = await self.import_data_for_date(date_str, db)
            results.append({
                "date": date_str,
                "result": result
            })
            current_date += timedelta(days=1)
        
        # Summary
        successful = sum(1 for r in results if r["result"]["success"])
        total_games = sum(r["result"].get("games_created", 0) for r in results)
        total_results = sum(r["result"].get("results_created", 0) for r in results)
        
        return {
            "success": True,
            "message": f"Processed {len(results)} dates",
            "successful_dates": successful,
            "failed_dates": len(results) - successful,
            "total_games_created": total_games,
            "total_results_created": total_results,
            "details": results
        }