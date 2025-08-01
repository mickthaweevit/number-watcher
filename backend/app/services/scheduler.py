import asyncio
import schedule
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import os
from .external_api import ExternalAPIService
from .external_api_v2 import ExternalAPIServiceV2

logger = logging.getLogger(__name__)

class LotteryScheduler:
    def __init__(self):
        self.is_running = False
        self.scheduler_thread = None
        self.external_api_url = os.getenv("EXTERNAL_API_URL")
        self.external_api_url_v2 = os.getenv("EXTERNAL_API_URL_V2")
        
    def start_scheduler(self):
        """Start the background scheduler"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        if not self.external_api_url and not self.external_api_url_v2:
            logger.warning("No external API URLs configured, scheduler will not start")
            return
        
        self.is_running = True
        
        # Schedule imports every 5 minutes
        schedule.every(5).minutes.do(self._run_scheduled_import)
        
        # Start scheduler in background thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("Lottery data scheduler started")
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        self.is_running = False
        schedule.clear()
        logger.info("Lottery data scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _run_scheduled_import(self):
        """Run the scheduled import job"""
        try:
            logger.info("Starting scheduled lottery data import")
            
            # Check if we're in the main thread or a background thread
            try:
                # Try to get the current event loop
                current_loop = asyncio.get_running_loop()
                # If we're here, there's already a loop running
                # Create a new thread to run the async code
                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        result = new_loop.run_until_complete(self._async_import())
                        if result["success"]:
                            logger.info(f"Scheduled import completed: {result['message']}")
                        else:
                            logger.error(f"Scheduled import failed: {result['message']}")
                    finally:
                        new_loop.close()
                
                thread = threading.Thread(target=run_in_thread, daemon=True)
                thread.start()
                thread.join()
                
            except RuntimeError:
                # No event loop running, we can create one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(self._async_import())
                    if result["success"]:
                        logger.info(f"Scheduled import completed: {result['message']}")
                    else:
                        logger.error(f"Scheduled import failed: {result['message']}")
                finally:
                    loop.close()
                
        except Exception as e:
            logger.error(f"Error in scheduled import: {str(e)}")
    
    async def _async_import(self) -> Dict[str, Any]:
        """Async import method for current date - imports from both APIs"""
        results = {"v1": None, "v2": None}
        
        # Import from V1 API if configured
        if self.external_api_url:
            try:
                today = datetime.now()
                api_date = (today - timedelta(days=1)).strftime('%Y-%m-%dT17:00:00.000Z')
                
                async with ExternalAPIService(base_url=self.external_api_url) as api_service:
                    results["v1"] = await api_service.import_live_data(api_date)
            except Exception as e:
                results["v1"] = {
                    "success": False,
                    "message": f"V1 import error: {str(e)}"
                }
        
        # Import from V2 API if configured
        if self.external_api_url_v2:
            try:
                today = datetime.now()
                api_date = today.strftime('%Y%m%d')
                
                from ..database import get_db
                db = next(get_db())
                
                try:
                    async with ExternalAPIServiceV2(base_url=self.external_api_url_v2) as api_service:
                        results["v2"] = await api_service.import_data_for_date(api_date, db)
                finally:
                    # Ensure database connection is closed
                    if db:
                        db.close()
            except Exception as e:
                results["v2"] = {
                    "success": False,
                    "message": f"V2 import error: {str(e)}"
                }
        
        # Combine results
        v1_success = results["v1"] and results["v1"].get("success", False)
        v2_success = results["v2"] and results["v2"].get("success", False)
        
        return {
            "success": v1_success or v2_success,
            "message": f"V1: {'✅' if v1_success else '❌'}, V2: {'✅' if v2_success else '❌'}",
            "v1_result": results["v1"],
            "v2_result": results["v2"]
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            "is_running": self.is_running,
            "external_api_configured": bool(self.external_api_url),
            "external_api_v2_configured": bool(self.external_api_url_v2),
            "next_jobs": [str(job) for job in schedule.jobs] if schedule.jobs else [],
            "thread_alive": self.scheduler_thread.is_alive() if self.scheduler_thread else False
        }
    
    def trigger_manual_import(self) -> Dict[str, Any]:
        """Manually trigger an import job"""
        try:
            logger.info("Manual import triggered")
            
            # Run in a separate thread to avoid event loop conflicts
            import_thread = threading.Thread(target=self._run_scheduled_import, daemon=True)
            import_thread.start()
            import_thread.join(timeout=60)  # Wait up to 60 seconds
            
            if import_thread.is_alive():
                return {"success": False, "message": "Manual import timed out"}
            
            return {"success": True, "message": "Manual import completed"}
        except Exception as e:
            logger.error(f"Manual import failed: {str(e)}")
            return {"success": False, "message": f"Manual import failed: {str(e)}"}
    
    def trigger_date_range_import(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Import data for a date range"""
        try:
            logger.info(f"Date range import triggered: {start_date} to {end_date}")
            
            # Parse dates
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            if start_dt > end_dt:
                return {"success": False, "message": "Start date must be before end date"}
            
            # Generate date list
            date_list = []
            current_dt = start_dt
            while current_dt <= end_dt:
                date_list.append(current_dt.strftime('%Y-%m-%dT%H:%M:%S.000Z'))
                current_dt += timedelta(days=1)
            
            if len(date_list) > 30:
                return {"success": False, "message": "Date range too large. Maximum 30 days allowed."}
            
            # Run import in separate thread
            result_container = {"result": None}
            
            def run_range_import():
                try:
                    result_container["result"] = self._run_date_range_import(date_list)
                except Exception as e:
                    result_container["result"] = {
                        "success": False,
                        "message": f"Date range import error: {str(e)}",
                        "total_dates": 0,
                        "successful_dates": 0,
                        "failed_dates": 0
                    }
            
            import_thread = threading.Thread(target=run_range_import, daemon=True)
            import_thread.start()
            import_thread.join(timeout=300)  # Wait up to 5 minutes for range import
            
            if import_thread.is_alive():
                return {"success": False, "message": "Date range import timed out"}
            
            return result_container["result"]
            
        except Exception as e:
            logger.error(f"Date range import failed: {str(e)}")
            return {"success": False, "message": f"Date range import failed: {str(e)}"}
    
    def _run_date_range_import(self, date_list: List[str]) -> Dict[str, Any]:
        """Run import for multiple dates"""
        successful_dates = 0
        failed_dates = 0
        total_games_created = 0
        total_results_updated = 0
        
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            for date_str in date_list:
                try:
                    logger.info(f"Importing data for date: {date_str}")
                    result = loop.run_until_complete(self._async_import_for_date(date_str))
                    
                    if result["success"]:
                        successful_dates += 1
                        total_games_created += result.get("games_created", 0)
                        total_results_updated += result.get("results_updated", 0)
                        logger.info(f"Successfully imported data for {date_str}")
                    else:
                        failed_dates += 1
                        logger.error(f"Failed to import data for {date_str}: {result['message']}")
                        
                except Exception as e:
                    failed_dates += 1
                    logger.error(f"Error importing data for {date_str}: {str(e)}")
                    
                # Small delay between requests to be nice to the API
                time.sleep(1)
                
        finally:
            loop.close()
        
        return {
            "success": True,
            "message": f"Date range import completed: {successful_dates} successful, {failed_dates} failed",
            "total_dates": len(date_list),
            "successful_dates": successful_dates,
            "failed_dates": failed_dates,
            "total_games_created": total_games_created,
            "total_results_updated": total_results_updated
        }
    
    async def _async_import_for_date(self, date_str: str) -> Dict[str, Any]:
        """Async import method for specific date - imports from both APIs"""
        results = {"v1": None, "v2": None}
        
        # Import from V1 API if configured
        if self.external_api_url:
            try:
                # Convert to previous day at 17:00 UTC
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                api_date = (date - timedelta(days=1)).strftime('%Y-%m-%dT17:00:00.000Z')
                
                async with ExternalAPIService(base_url=self.external_api_url) as api_service:
                    results["v1"] = await api_service.import_live_data(api_date)
            except Exception as e:
                results["v1"] = {
                    "success": False,
                    "message": f"V1 import error for {date_str}: {str(e)}"
                }
        
        # Import from V2 API if configured
        if self.external_api_url_v2:
            try:
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                api_date = date.strftime('%Y%m%d')
                
                from ..database import get_db
                db = next(get_db())
                
                try:
                    async with ExternalAPIServiceV2(base_url=self.external_api_url_v2) as api_service:
                        results["v2"] = await api_service.import_data_for_date(api_date, db)
                finally:
                    if db:
                        db.close()
            except Exception as e:
                results["v2"] = {
                    "success": False,
                    "message": f"V2 import error for {date_str}: {str(e)}"
                }
        
        # Combine results
        v1_success = results["v1"] and results["v1"].get("success", False)
        v2_success = results["v2"] and results["v2"].get("success", False)
        
        # Calculate totals from both APIs
        total_games_created = 0
        total_results_updated = 0
        
        if v1_success:
            total_games_created += results["v1"].get("games_created", 0)
            total_results_updated += results["v1"].get("results_updated", 0)
        
        if v2_success:
            total_games_created += results["v2"].get("games_created", 0)
            total_results_updated += results["v2"].get("results_updated", 0)
        
        return {
            "success": v1_success or v2_success,
            "message": f"V1: {'✅' if v1_success else '❌'}, V2: {'✅' if v2_success else '❌'}",
            "games_created": total_games_created,
            "results_updated": total_results_updated,
            "total_records": total_games_created + total_results_updated,
            "v1_result": results["v1"],
            "v2_result": results["v2"]
        }

# Global scheduler instance
lottery_scheduler = LotteryScheduler()