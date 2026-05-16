import { create } from 'zustand'

export type AppView = 'menu' | 'setup' | 'game' | 'results' | 'history'
export type GameType = 'trivia'
export type SetupMode = 'solo' | 'hotseat'

type AppState = {
  selectedGame: GameType
  setupMode: SetupMode
  view: AppView
  openHistory: () => void
  selectGame: (game: GameType) => void
  resetToMenu: () => void
  selectMode: (mode: SetupMode) => void
  setView: (view: AppView) => void
}

/** Store lightweight app navigation state outside the game socket state. */
export const useAppStore = create<AppState>((set) => ({
  selectedGame: 'trivia',
  setupMode: 'hotseat',
  view: 'menu',
  openHistory: () => set({ view: 'history' }),
  resetToMenu: () => set({ view: 'menu' }),
  selectGame: (game) => set({ selectedGame: game }),
  selectMode: (mode) => set({ setupMode: mode, view: 'setup' }),
  setView: (view) => set({ view }),
}))
