from datetime import datetime
from typing import Dict, List, Tuple, Optional

def parse_game_code(game_code: str) -> Tuple[str, str]:
    """
    Parse game code to extract base game ID and date
    Example: "L03-01-000500-20250622" -> ("L03-01-000500", "2025-06-22")
    """
    parts = game_code.split('-')
    date_part = parts[-1]  # "20250622"
    base_id = '-'.join(parts[:-1])  # "L03-01-000500"
    
    # Convert date: "20250622" -> "2025-06-22"
    formatted_date = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
    
    return base_id, formatted_date

def process_api_result(result_value: Optional[str]) -> Tuple[str, Optional[str]]:
    """
    Process API result value and determine status
    Returns: (status, processed_value)
    """
    if not result_value:
        return "no_result", None
    
    if result_value == "รอผล":
        return "waiting", result_value
    elif result_value == "ยกเลิก":
        return "cancelled", result_value
    elif result_value and result_value.replace('-', '').isdigit():
        return "completed", result_value
    else:
        return "no_result", None

def process_api_response(api_data: Dict) -> List[Dict]:
    """
    Process the complete API response and extract game data
    Returns list of processed game records
    """
    processed_games = []
    
    # Process each category in the API response
    for category, category_data in api_data.items():
        if not isinstance(category_data, dict) or 'lists' not in category_data:
            continue
            
        date_game = category_data.get('DATE_GAME', '')
        
        for game_item in category_data['lists']:
            # Extract base game ID and date from GAME_CODE
            game_code = game_item.get('GAME_CODE', '')
            if not game_code:
                continue
                
            base_game_id, result_date = parse_game_code(game_code)
            
            # Process results
            result_3up_status, result_3up = process_api_result(game_item.get('RESULT_3UP'))
            result_2down_status, result_2down = process_api_result(game_item.get('RESULT_2DOWN'))
            result_4up_status, result_4up = process_api_result(game_item.get('RESULT_4UP'))
            
            # Determine overall status (prioritize waiting/cancelled over completed)
            if any(status in ['waiting', 'cancelled'] for status in [result_3up_status, result_2down_status, result_4up_status]):
                overall_status = next(status for status in [result_3up_status, result_2down_status, result_4up_status] 
                                    if status in ['waiting', 'cancelled'])
            else:
                overall_status = "completed" if any(status == "completed" for status in [result_3up_status, result_2down_status, result_4up_status]) else "no_result"
            
            processed_game = {
                'base_game_id': base_game_id,
                'game_name': game_item.get('GAME_NAME', ''),
                'full_game_code': game_code,
                'result_date': result_date,
                'result_3up': result_3up,
                'result_2down': result_2down,
                'result_4up': result_4up,
                'status': overall_status
            }
            
            processed_games.append(processed_game)
    
    return processed_games