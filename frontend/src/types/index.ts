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

export interface TableData {
  gameName: string;
  gameId: number;
  category: string;
  countryCode: string | null;
  results: { [date: string]: string };
}