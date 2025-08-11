import React, { createContext, useContext, useState, useEffect } from "react";

const THEMES = [
  { key: "dark-hacker", label: "Dark Hacker", css: "/src/styles/dark-hacker.css" },
  { key: "terminal", label: "Terminal", css: "/src/styles/terminal.css" },
  { key: "matrix", label: "Matrix", css: "/src/styles/matrix.css" },
  { key: "retro", label: "Retro", css: "/src/styles/retro.css" },
];

export const ThemeContext = createContext({
  theme: "dark-hacker",
  setTheme: () => {},
  themes: THEMES
});

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => localStorage.getItem("theme") || "dark-hacker");

  useEffect(() => {
    // Dynamically inject the theme stylesheet
    const themeObj = THEMES.find(t => t.key === theme) || THEMES[0];
    let link = document.getElementById("dynamic-theme-css");
    if (!link) {
      link = document.createElement("link");
      link.id = "dynamic-theme-css";
      link.rel = "stylesheet";
      document.head.appendChild(link);
    }
    link.href = themeObj.css;
    document.body.className = theme; // for global styling
    localStorage.setItem("theme", theme);
    return () => {};
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme, themes: THEMES }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}