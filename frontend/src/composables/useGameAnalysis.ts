import { ref, computed } from 'vue'
import type { Game, Result } from '../types'

export interface PatternAnalysis {
  betAmount: number
  wins: number
  losses: number
  winAmount: number
  lossAmount: number
  netAmount: number
  monthlyBreakdown: { [month: string]: { wins: number, losses: number, netAmount: number } }
}

export interface GameAnalysis {
  game: Game
  calculate: boolean
  totalResults: number
  patterns: {
    first_two: PatternAnalysis
    first_third: PatternAnalysis
    last_two: PatternAnalysis
  }
  // Legacy fields for compatibility
  patternMatches: number
  winAmount: number
  lossAmount: number
  netAmount: number
  monthlyBreakdown: { [month: string]: { wins: number, losses: number, netAmount: number } }
}

export const useGameAnalysis = () => {
  const analysisCache = new Map<string, GameAnalysis>()

  const createEmptyPatternAnalysis = (): PatternAnalysis => ({
    betAmount: 0,
    wins: 0,
    losses: 0,
    winAmount: 0,
    lossAmount: 0,
    netAmount: 0,
    monthlyBreakdown: {}
  })

  const updatePatternAnalysis = (pattern: PatternAnalysis, month: string, isWin: boolean) => {
    if (!pattern.monthlyBreakdown[month]) {
      pattern.monthlyBreakdown[month] = { wins: 0, losses: 0, netAmount: 0 }
    }
    
    if (isWin) {
      pattern.wins++
      pattern.monthlyBreakdown[month].wins++
    } else {
      pattern.losses++
      pattern.monthlyBreakdown[month].losses++
    }
  }

  const analyzeGameOptimized = (game: Game, results: Result[]): GameAnalysis => {
    const totalResults = results.length
    
    const patterns = {
      first_two: createEmptyPatternAnalysis(),
      first_third: createEmptyPatternAnalysis(), 
      last_two: createEmptyPatternAnalysis()
    }
    
    for (const result of results) {
      if (!result.result_3up || result.result_3up.length !== 3) continue
      
      const [d1, d2, d3] = result.result_3up.split('')
      const month = result.result_date.slice(0, 7)
      
      // Check each pattern
      if (d1 === d2 && d2 !== d3) {
        updatePatternAnalysis(patterns.first_two, month, true)
      } else {
        updatePatternAnalysis(patterns.first_two, month, false)
      }
      
      if (d1 === d3 && d1 !== d2) {
        updatePatternAnalysis(patterns.first_third, month, true)
      } else {
        updatePatternAnalysis(patterns.first_third, month, false)
      }
      
      if (d2 === d3 && d1 !== d2) {
        updatePatternAnalysis(patterns.last_two, month, true)
      } else {
        updatePatternAnalysis(patterns.last_two, month, false)
      }
    }
    
    return {
      game,
      calculate: true,
      totalResults,
      patterns,
      // Legacy fields for compatibility
      patternMatches: 0,
      winAmount: 0,
      lossAmount: 0,
      netAmount: 0,
      monthlyBreakdown: {}
    }
  }

  const recalculateGame = (gameAnalysis: GameAnalysis) => {
    Object.values(gameAnalysis.patterns).forEach(pattern => {
      const dailyBetAmount = 90 * pattern.betAmount
      pattern.winAmount = pattern.wins * pattern.betAmount * 1000
      pattern.lossAmount = gameAnalysis.totalResults * dailyBetAmount
      pattern.netAmount = pattern.winAmount - pattern.lossAmount
      
      Object.values(pattern.monthlyBreakdown).forEach(monthData => {
        monthData.netAmount = (monthData.wins * pattern.betAmount * 1000) - ((monthData.wins + monthData.losses) * dailyBetAmount)
      })
    })
  }

  const getTotalWins = (gameAnalysis: GameAnalysis): number => {
    return Object.values(gameAnalysis.patterns).reduce((sum, pattern) => {
      return sum + (pattern.betAmount > 0 ? pattern.wins : 0)
    }, 0)
  }

  const getTotalWinAmount = (gameAnalysis: GameAnalysis): number => {
    return Object.values(gameAnalysis.patterns).reduce((sum, pattern) => {
      return sum + (pattern.betAmount > 0 ? pattern.winAmount : 0)
    }, 0)
  }

  const getTotalLossAmount = (gameAnalysis: GameAnalysis): number => {
    return Object.values(gameAnalysis.patterns).reduce((sum, pattern) => {
      return sum + (pattern.betAmount > 0 ? pattern.lossAmount : 0)
    }, 0)
  }

  const getTotalNetAmount = (gameAnalysis: GameAnalysis): number => {
    return Object.values(gameAnalysis.patterns).reduce((sum, pattern) => {
      return sum + (pattern.betAmount > 0 ? pattern.netAmount : 0)
    }, 0)
  }

  const getMonthlyData = (gameAnalysis: GameAnalysis) => {
    const allMonths = new Set<string>()
    Object.values(gameAnalysis.patterns).forEach(pattern => {
      if (pattern.betAmount > 0) {
        Object.keys(pattern.monthlyBreakdown).forEach(month => allMonths.add(month))
      }
    })
    
    return Array.from(allMonths).map(month => {
      const firstTwo = gameAnalysis.patterns.first_two.betAmount > 0 ? {
        wins: gameAnalysis.patterns.first_two.monthlyBreakdown[month]?.wins || 0,
        losses: gameAnalysis.patterns.first_two.monthlyBreakdown[month]?.losses || 0
      } : { wins: 0, losses: 0 }
      
      const firstThird = gameAnalysis.patterns.first_third.betAmount > 0 ? {
        wins: gameAnalysis.patterns.first_third.monthlyBreakdown[month]?.wins || 0,
        losses: gameAnalysis.patterns.first_third.monthlyBreakdown[month]?.losses || 0
      } : { wins: 0, losses: 0 }
      
      const lastTwo = gameAnalysis.patterns.last_two.betAmount > 0 ? {
        wins: gameAnalysis.patterns.last_two.monthlyBreakdown[month]?.wins || 0,
        losses: gameAnalysis.patterns.last_two.monthlyBreakdown[month]?.losses || 0
      } : { wins: 0, losses: 0 }
      
      let netAmount = 0
      if (gameAnalysis.patterns.first_two.betAmount > 0) netAmount += gameAnalysis.patterns.first_two.monthlyBreakdown[month]?.netAmount || 0
      if (gameAnalysis.patterns.first_third.betAmount > 0) netAmount += gameAnalysis.patterns.first_third.monthlyBreakdown[month]?.netAmount || 0
      if (gameAnalysis.patterns.last_two.betAmount > 0) netAmount += gameAnalysis.patterns.last_two.monthlyBreakdown[month]?.netAmount || 0
      
      return {
        month,
        firstTwo,
        firstThird, 
        lastTwo,
        allWins: firstTwo.wins + firstThird.wins + lastTwo.wins,
        allLosses: firstTwo.losses + firstThird.losses + lastTwo.losses,
        netAmount
      }
    }).sort((a, b) => a.month.localeCompare(b.month))
  }

  return {
    analysisCache,
    analyzeGameOptimized,
    recalculateGame,
    getTotalWins,
    getTotalWinAmount,
    getTotalLossAmount,
    getTotalNetAmount,
    getMonthlyData
  }
}