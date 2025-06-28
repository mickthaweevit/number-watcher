export interface Game {
  id: number;
  base_game_id: string;
  game_name: string;
  country_code: string | null;
  category: string;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface Result {
  id: number;
  game_id: number;
  full_game_code: string;
  result_date: string;
  result_3up: string | null;
  result_2down: string | null;
  result_4up: string | null;
  status: string;
  created_at: string;
  updated_at: string | null;
  game: Game;
}

export interface DateResult {
  result_2down: string | null;
  result_3up: string | null;
  result_4up: string | null;
  status: string;
  hasData: boolean; // Track if game has data for future features
}

export interface TableData {
  gameName: string;
  gameId: number;
  category: string;
  countryCode: string | null;
  results: { [date: string]: DateResult };
}

export interface ImportLog {
  id: number;
  filename: string | null;
  import_type: string;
  started_at: string;
  completed_at: string | null;
  status: string;
  records_processed: number;
  games_created: number;
  results_created: number;
  error_message: string | null;
  file_size: number | null;
}

export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
  last_login?: string;
}

export interface DashboardProfile {
  id: number;
  user_id: number;
  profile_name: string;
  bet_amount: number;
  selected_patterns: string[];
  selected_game_ids: number[];
  created_at: string;
  updated_at: string;
}