import { createTheme } from '@mui/material/styles'

/** Material UI theme aligned with the current Party Buddy palette. */
export const appTheme = createTheme({
  palette: {
    background: {
      default: '#f4f6f8',
      paper: '#ffffff',
    },
    error: {
      main: '#be123c',
    },
    primary: {
      main: '#0f766e',
    },
    text: {
      primary: '#111827',
      secondary: '#6b7280',
    },
    warning: {
      main: '#d97706',
    },
  },
  shape: {
    borderRadius: 8,
  },
  typography: {
    fontFamily: "system-ui, 'Segoe UI', Roboto, sans-serif",
    button: {
      fontWeight: 800,
      letterSpacing: 0,
      textTransform: 'none',
    },
  },
})
