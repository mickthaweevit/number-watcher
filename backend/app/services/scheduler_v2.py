import asyncio
import schedule
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import os
from .external_api_v2 import ExternalAPIServiceV2

logger = logging.getLogger(__name__)

class LotterySchedulerV2:
    def __init__(self):
        self.is_running = False
        self.scheduler_thread = None
        self.external_api_url_v2 = os.getenv("EXTERNAL_API_URL_V2")
        
    def start_scheduler(self):
        """Start the background scheduler for v2 API"""
        if self.is_running:
            logger.warning("V2 Scheduler is already running")
            return
        
        if not self.external_api_url_v2:
            logger.warning("EXTERNAL_API_URL_V2 not configured, v2 scheduler will not start")
            return
        
        self.is_running = True
        
        # Schedule imports every 5 minutes (offset by 2.5 minutes from v1)
        schedule.every(5).minutes.at(":02:30").do(self._run_scheduled_import)
        
        # Start scheduler in background thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("V2 Lottery data scheduler started")
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        self.is_running = False
        schedule.clear()
        logger.info("V2 Lottery data scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def _run_scheduled_import(self):
        """Run the scheduled import job"""
        try:
            logger.info("Starting scheduled v2 lottery data import")
            
            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    result = new_loop.run_until_complete(self._async_import())
                    if result["success"]:
                        logger.info(f"V2 Scheduled import completed: {result['message']}")
                    else:
                        logger.error(f"V2 Scheduled import failed: {result['message']}")
                finally:
                    new_loop.close()
            
            thread = threading.Thread(target=run_in_thread, daemon=True)
            thread.start()
            thread.join()
                
        except Exception as e:
            logger.error(f"Error in v2 scheduled import: {str(e)}")
    
    async def _async_import(self) -> Dict[str, Any]:
        """Async import method for current date"""
        try:
            # Get current date in YYYYMMDD format
            today = datetime.now()
            api_date = today.strftime('%Y%m%d')
            
            from ..database import get_db
            db = next(get_db())
            
            async with ExternalAPIServiceV2(base_url=self.external_api_url_v2) as api_service:
                result = await api_service.import_data_for_date(api_date, db)
                return result
        except Exception as e:
            return {
                "success": False,
                "message": f"V2 Scheduled import error: {str(e)}",
                "games_created": 0,
                "results_created": 0,
                "total_records": 0
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get v2 scheduler status"""
        return {
            "is_running": self.is_running,
            "external_api_v2_configured": bool(self.external_api_url_v2),
            "next_jobs": [str(job) for job in schedule.jobs] if schedule.jobs else [],
            "thread_alive": self.scheduler_thread.is_alive() if self.scheduler_thread else False
        }
    
    def trigger_manual_import(self) -> Dict[str, Any]:
        """Manually trigger a v2 import job"""
        try:
            logger.info("V2 Manual import triggered")
            
            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    result = new_loop.run_until_complete(self._async_import())
                    return result
                finally:
                    new_loop.close()
            
            import_thread = threading.Thread(target=run_in_thread, daemon=True)
            import_thread.start()
            import_thread.join(timeout=60)
            
            if import_thread.is_alive():
                return {"success": False, "message": "V2 Manual import timed out"}
            
            return {"success": True, "message": "V2 Manual import completed"}
        except Exception as e:
            logger.error(f"V2 Manual import failed: {str(e)}")
            return {"success": False, "message": f"V2 Manual import failed: {str(e)}"}

# Global v2 scheduler instance
lottery_scheduler_v2 = LotterySchedulerV2()