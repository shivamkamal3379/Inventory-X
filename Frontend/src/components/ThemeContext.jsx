import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

const ThemeContext = createContext(null);
const STORAGE_KEY = 'inventoryx.theme';

function systemPrefersDark() {
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false;
}

/**
 * Three states: 'light', 'dark', and 'system'. 'system' is the default and
 * tracks the OS setting live, so a user whose machine switches to dark in the
 * evening does not also have to switch this app.
 */
export function ThemeProvider({ children }) {
  const [preference, setPreference] = useState(() => {
    if (typeof window === 'undefined') return 'system';
    return localStorage.getItem(STORAGE_KEY) || 'system';
  });

  // Only the OS signal is stored. The effective theme is derived below rather
  // than held in a second state, which keeps the two from drifting apart and
  // avoids a setState inside an effect.
  const [systemDark, setSystemDark] = useState(systemPrefersDark);

  const theme = preference === 'system' ? (systemDark ? 'dark' : 'light') : preference;

  // Subscribe to the OS preference.
  useEffect(() => {
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const onChange = (e) => setSystemDark(e.matches);
    mq.addEventListener('change', onChange);
    return () => mq.removeEventListener('change', onChange);
  }, []);

  // Push the resolved theme out to the DOM and to storage — genuine external
  // systems, which is what an effect is for.
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    document.documentElement.style.colorScheme = theme;
  }, [theme]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, preference);
  }, [preference]);

  const toggle = useCallback(() => {
    setPreference(theme === 'dark' ? 'light' : 'dark');
  }, [theme]);

  const value = useMemo(
    () => ({ preference, setPreference, theme, toggle }),
    [preference, theme, toggle],
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used inside a ThemeProvider');
  return ctx;
}
