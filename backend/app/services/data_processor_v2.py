from typing import Dict, Any, List
from datetime import datetime
import re

def process_api_response_v2(api_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process new API format response and convert to standardized format
    
    Expected input format:
    {
        "success": true,
        "info": [
            {
                "productId": 1,
                "productNameTh": "หวยรัฐบาลไทย",
                "productCode": "TH",
                "periodId": 375679,
                "periodName": "วันจันทร์ 16/06/68",
                "award1": "507392",
                "award2": "06",
                "award3": "243, 017",
                "award4": "299, 736",
                "ykRound": 0,
                "ykDate": "20250626"
            }
        ]
    }
    """
    
    if not api_data.get("success") or not api_data.get("info"):
        return []
    
    processed_games = []
    
    # Filter out unwanted product codes
    filtered_products = [
        item for item in api_data["info"] 
        if item.get("productCode") not in ["YK", "YK5", "TH"]
    ]
    
    for item in filtered_products:
        try:
            # Parse date from periodName (e.g., "วันจันทร์ 16/06/68")
            result_date = parse_period_date(item.get("periodName", ""))
            
            if not result_date:
                continue  # Skip if can't parse date
            
            # Create game data
            game_data = {
                "product_id": item.get("productId"),
                "product_name_th": item.get("productNameTh", ""),
                "product_code": item.get("productCode", ""),
                "period_id": item.get("periodId"),
                "period_name": item.get("periodName", ""),
                "result_date": result_date,
                "award1": clean_award_value(item.get("award1", "")),
                "award2": clean_award_value(item.get("award2", "")),
                "award3": clean_award_value(item.get("award3", "")),
                "award4": clean_award_value(item.get("award4", "")),
                "yk_round": item.get("ykRound", 0),
                "status": "completed"  # Default status
            }
            
            # Skip if no valid awards
            if not any([game_data["award1"], game_data["award2"], game_data["award3"]]):
                continue
                
            processed_games.append(game_data)
            
        except Exception as e:
            print(f"Error processing item {item}: {str(e)}")
            continue
    
    return processed_games

def parse_period_date(period_name: str) -> str:
    """
    Parse Thai date format to ISO date
    Example: "วันจันทร์ 16/06/68" -> "2025-06-16"
    """
    if not period_name:
        return ""
    
    try:
        # Extract date pattern DD/MM/YY
        date_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{2})', period_name)
        if not date_match:
            return ""
        
        day, month, year = date_match.groups()
        
        # Convert 2-digit year to 4-digit (assuming 68 = 2025, etc.)
        year_int = int(year)
        if year_int >= 68:  # Adjust threshold as needed
            full_year = 2000 + year_int
        else:
            full_year = 2100 + year_int
        
        # Format as ISO date
        return f"{full_year}-{month.zfill(2)}-{day.zfill(2)}"
        
    except Exception as e:
        print(f"Error parsing date from '{period_name}': {str(e)}")
        return ""

def clean_award_value(value: str) -> str:
    """
    Clean award values - remove 'xxx' and extra spaces
    """
    if not value or value.strip().lower() in ['xxx', 'xx', '']:
        return ""
    
    # Clean up the value
    cleaned = value.strip()
    
    # Remove 'xxx' patterns
    if 'xxx' in cleaned.lower():
        return ""
    
    return cleaned