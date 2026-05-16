import { create } from 'zustand'

export type AppView = 'menu' | 'setup' | 'game' | 'results' | 'history'
export type SetupMode = 'solo' | 'hotseat'

type AppState = {
  setupMode: SetupMode
  view: AppView
  openHistory: () => void
  resetToMenu: () => void
  selectMode: (mode: SetupMode) => void
  setView: (view: AppView) => void
}

/** Store lightweight app navigation state outside the game socket state. */
export const useAppStore = create<AppState>((set) => ({
  setupMode: 'hotseat',
  view: 'menu',
  openHistory: () => set({ view: 'history' }),
  resetToMenu: () => set({ view: 'menu' }),
  selectMode: (mode) => set({ setupMode: mode, view: 'setup' }),
  setView: (view) => set({ view }),
}))
