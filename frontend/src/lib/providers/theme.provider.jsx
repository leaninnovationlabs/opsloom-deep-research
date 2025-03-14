import { useMemo } from "react"
import { createContext, useContext, useEffect, useState } from "react"
import { FORCED_THEME } from "../constants"

const initialState = {
    theme: "system",
    setTheme: () => null,
    rawTheme: "null"
}

const ThemeProviderContext = createContext(initialState)

export function ThemeProvider({ children, storageKey = "vite-ui-theme", ...props }) {
    const [theme, setTheme] = useState(
        () => (localStorage.getItem(storageKey)) || FORCED_THEME ? FORCED_THEME : "system"
    )

    const [rawTheme, setRawTheme] = useState(null) //dark or light (no system)

    useEffect(() => {
        const root = window.document.documentElement

        root.classList.remove("light", "dark")

        if (theme === "system") {
            const systemTheme = window.matchMedia("(prefers-color-scheme: dark)")
                .matches
                ? "dark"
                : "light"

            root.classList.add(systemTheme)
            setRawTheme(systemTheme)
            return
        }

        root.classList.add(theme)
        setRawTheme(theme)
    }, [theme])

    const value = useMemo(() => ({
        theme,
        rawTheme,
        setTheme: (theme) => {
            localStorage.setItem(storageKey, theme)
            setTheme(theme)
        },
    }), [rawTheme, theme])

    return (
        <ThemeProviderContext.Provider {...props} value={value}>
            {children}
        </ThemeProviderContext.Provider>
    )
}

export const useTheme = () => {
    const context = useContext(ThemeProviderContext)

    if (context === undefined)
        throw new Error("useTheme must be used within a ThemeProvider")

    return context
}
