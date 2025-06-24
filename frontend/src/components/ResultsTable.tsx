import React, { useState, useEffect } from 'react';
import { gameApi } from '../services/api';
import { Result, TableData } from '../types';

const ResultsTable: React.FC = () => {
  const [results, setResults] = useState<Result[]>([]);
  const [tableData, setTableData] = useState<TableData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    fetchResults();
  }, []);

  const fetchResults = async () => {
    try {
      setLoading(true);
      const data = await gameApi.getAllResults();
      setResults(data);
      transformDataForTable(data);
    } catch (err) {
      setError('Failed to fetch results');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const transformDataForTable = (results: Result[]) => {
    // Group results by game
    const gameMap = new Map<number, TableData>();
    const allDates = new Set<string>();

    results.forEach(result => {
      allDates.add(result.result_date);
      
      if (!gameMap.has(result.game_id)) {
        gameMap.set(result.game_id, {
          gameName: result.game.game_name,
          gameId: result.game_id,
          category: result.game.category,
          countryCode: result.game.country_code,
          results: {}
        });
      }

      const gameData = gameMap.get(result.game_id)!;
      
      // Format result display
      let resultDisplay = '';
      if (result.status === 'waiting') {
        resultDisplay = 'รอผล';
      } else if (result.status === 'cancelled') {
        resultDisplay = 'ยกเลิก';
      } else if (result.status === 'completed') {
        const parts = [];
        if (result.result_3up) parts.push(result.result_3up);
        if (result.result_2down) parts.push(result.result_2down);
        if (result.result_4up) parts.push(result.result_4up);
        resultDisplay = parts.join('/') || '-';
      } else {
        resultDisplay = '-';
      }

      gameData.results[result.result_date] = resultDisplay;
    });

    setTableData(Array.from(gameMap.values()));
  };

  const getUniqueCategories = () => {
    const categories = new Set(results.map(r => r.game.category));
    return Array.from(categories);
  };

  const getUniqueDates = () => {
    const dates = new Set(results.map(r => r.result_date));
    return Array.from(dates).sort();
  };

  const filteredTableData = selectedCategory === 'all' 
    ? tableData 
    : tableData.filter(game => game.category === selectedCategory);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  const uniqueDates = getUniqueDates();
  const categories = getUniqueCategories();

  return (
    <div style={{ padding: '20px' }}>
      <h2>NumWatch Results Table</h2>
      
      {/* Category Filter */}
      <div style={{ marginBottom: '20px' }}>
        <label>Filter by Category: </label>
        <select 
          value={selectedCategory} 
          onChange={(e) => setSelectedCategory(e.target.value)}
          style={{ marginLeft: '10px', padding: '5px' }}
        >
          <option value="all">All Categories</option>
          {categories.map(category => (
            <option key={category} value={category}>{category}</option>
          ))}
        </select>
      </div>

      {/* Results Table */}
      <div style={{ overflowX: 'auto' }}>
        <table style={{ 
          borderCollapse: 'collapse', 
          width: '100%', 
          border: '1px solid #ddd' 
        }}>
          <thead>
            <tr style={{ backgroundColor: '#f5f5f5' }}>
              <th style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'left' }}>
                Game Name
              </th>
              <th style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'left' }}>
                Category
              </th>
              <th style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'left' }}>
                Country
              </th>
              {uniqueDates.map(date => (
                <th key={date} style={{ border: '1px solid #ddd', padding: '8px', textAlign: 'center' }}>
                  {date}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredTableData.map(game => (
              <tr key={game.gameId}>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                  {game.gameName}
                </td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                  {game.category}
                </td>
                <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                  {game.countryCode || '-'}
                </td>
                {uniqueDates.map(date => (
                  <td key={date} style={{ 
                    border: '1px solid #ddd', 
                    padding: '8px', 
                    textAlign: 'center',
                    backgroundColor: game.results[date] === 'รอผล' ? '#fff3cd' : 
                                   game.results[date] === 'ยกเลิก' ? '#f8d7da' : 'white'
                  }}>
                    {game.results[date] || '-'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
        Showing {filteredTableData.length} games • Total results: {results.length}
      </div>
    </div>
  );
};

export default ResultsTable;