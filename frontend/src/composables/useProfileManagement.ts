import { ref, computed } from 'vue'
import { profileApi } from '../services/api'
import type { DashboardProfile } from '../types'
import type { GameAnalysis } from './useGameAnalysis'

export const useProfileManagement = () => {
  const profiles = ref<DashboardProfile[]>([])
  const selectedProfileId = ref<number | null>(null)
  const profilesLoading = ref(false)
  const profileLoading = ref(false)
  const loadedProfileState = ref<any>(null)
  const hasUnsavedChanges = ref(false)
  
  let loadProfileAbortController: AbortController | null = null

  const fetchProfiles = async (dashboardType: string = 'nhl_dashboard') => {
    profilesLoading.value = true
    try {
      profiles.value = await profileApi.getProfiles(dashboardType)
    } catch (error) {
      console.error('Failed to fetch profiles:', error)
    } finally {
      profilesLoading.value = false
    }
  }

  const buildProfileData = (
    profileName: string,
    selectedPatterns: string[],
    selectedGames: GameAnalysis[]
  ) => ({
    profile_name: profileName,
    bet_amount: 0,
    selected_patterns: selectedPatterns,
    selected_game_ids: selectedGames.map(g => g.game.id),
    game_pattern_bets: selectedGames.reduce((acc, game) => {
      acc[game.game.id] = {
        first_two: game.patterns.first_two.betAmount || 0,
        first_third: game.patterns.first_third.betAmount || 0,
        last_two: game.patterns.last_two.betAmount || 0
      }
      return acc
    }, {} as Record<number, any>)
  })

  const saveCurrentProfile = async (
    selectedPatterns: string[],
    selectedGames: GameAnalysis[],
    profileData: any = null,
    dashboardType: string = 'nhl_dashboard'
  ) => {
    if (!selectedProfileId.value) return false
    
    try {
      const profileName = profiles.value.find(p => p.id === selectedProfileId.value)?.profile_name || ''
      const finalProfileData = profileData || buildProfileData(profileName, selectedPatterns, selectedGames)
      finalProfileData.dashboard_type = dashboardType
      
      await profileApi.updateProfile(selectedProfileId.value, finalProfileData)
      await fetchProfiles(dashboardType)
      
      updateLoadedState(selectedPatterns, selectedGames)
      hasUnsavedChanges.value = false
      alert('บันทึกโปรไฟล์สำเร็จแล้ว!')
      return true
    } catch (error) {
      alert('บันทึกโปรไฟล์ล้มเหลว')
      return false
    }
  }

  const saveAsNewProfile = async (
    profileName: string,
    selectedPatterns: string[],
    selectedGames: GameAnalysis[],
    profileData: any = null,
    dashboardType: string = 'nhl_dashboard'
  ) => {
    if (!profileName.trim()) {
      alert('กรุณากรอกชื่อโปรไฟล์')
      return false
    }
    
    try {
      const finalProfileData = profileData || buildProfileData(profileName, selectedPatterns, selectedGames)
      finalProfileData.profile_name = profileName
      finalProfileData.dashboard_type = dashboardType
      await profileApi.createProfile(finalProfileData)
      await fetchProfiles(dashboardType)
      alert('สร้างโปรไฟล์ใหม่สำเร็จแล้ว!')
      return true
    } catch (error) {
      alert('สร้างโปรไฟล์ล้มเหลว ชื่ออาจถูกใช้แล้ว')
      return false
    }
  }

  const deleteProfile = async () => {
    if (!selectedProfileId.value) return false
    
    const profile = profiles.value.find(p => p.id === selectedProfileId.value)
    if (!profile) return false
    
    if (confirm(`Delete profile "${profile.profile_name}"?`)) {
      try {
        await profileApi.deleteProfile(selectedProfileId.value)
        await fetchProfiles('nhl_dashboard') // Default for delete since we don't know the type
        selectedProfileId.value = null
        alert('Profile deleted successfully!')
        return true
      } catch (error) {
        alert('Failed to delete profile')
        return false
      }
    }
    return false
  }

  const updateLoadedState = (selectedPatterns: string[], selectedGames: GameAnalysis[]) => {
    loadedProfileState.value = {
      selectedPatterns: [...selectedPatterns],
      selectedGameIds: [...selectedGames.map(g => g.game.id)],
      gamePatternBets: selectedGames.reduce((acc, game) => {
        acc[game.game.id] = {
          first_two: game.patterns.first_two.betAmount,
          first_third: game.patterns.first_third.betAmount,
          last_two: game.patterns.last_two.betAmount
        }
        return acc
      }, {} as Record<number, any>)
    }
  }

  const checkForUnsavedChanges = (selectedPatterns: string[], selectedGames: GameAnalysis[]) => {
    if (!loadedProfileState.value) return false
    
    const arraysEqual = (a: any[], b: any[]) => {
      return a.length === b.length && a.every((val, i) => val === b[i])
    }
    
    const currentGameBets = selectedGames.reduce((acc, game) => {
      acc[game.game.id] = {
        first_two: game.patterns.first_two.betAmount,
        first_third: game.patterns.first_third.betAmount,
        last_two: game.patterns.last_two.betAmount
      }
      return acc
    }, {} as Record<number, any>)
    
    const savedGameBets = loadedProfileState.value.gamePatternBets || {}
    const gameBetsChanged = JSON.stringify(currentGameBets) !== JSON.stringify(savedGameBets)
    
    return (
      !arraysEqual(selectedPatterns, loadedProfileState.value.selectedPatterns) ||
      !arraysEqual(selectedGames.map(g => g.game.id), loadedProfileState.value.selectedGameIds) ||
      gameBetsChanged
    )
  }

  const canSaveCurrent = computed(() => {
    return selectedProfileId.value !== null && hasUnsavedChanges.value
  })

  const clearProfile = () => {
    selectedProfileId.value = null
    loadedProfileState.value = null
    hasUnsavedChanges.value = false
  }

  const cancelProfileLoad = () => {
    if (loadProfileAbortController) {
      loadProfileAbortController.abort()
      loadProfileAbortController = null
    }
  }

  return {
    profiles,
    selectedProfileId,
    profilesLoading,
    profileLoading,
    hasUnsavedChanges,
    canSaveCurrent,
    fetchProfiles,
    saveCurrentProfile,
    saveAsNewProfile,
    deleteProfile,
    updateLoadedState,
    checkForUnsavedChanges,
    clearProfile,
    cancelProfileLoad,
    loadedProfileState,
    loadProfileAbortController: () => loadProfileAbortController,
    setLoadProfileAbortController: (controller: AbortController | null) => {
      loadProfileAbortController = controller
    },
    setProfileLoading: (loading: boolean) => {
      profileLoading.value = loading
    }
  }
}