import { create } from 'zustand';
import { getAppConfig, getAccount } from '@/lib/api';
import { getGreeting } from '@/lib/utils';

const MIN_LOAD_TIME = 500; // Force load screen so it doesn't flash

const INIT = {
    ready: false,
    requiresEmail: null,
    shortCode: null, //e.g. swi, lil, etc
    palette: null,
    logo: { dark: null, light: null },
    fatal: false,
}

const useAppConfigStore = create((set, get) => ({

    ...INIT,

    initStore: async (shortCode) => {

        try {

            const config = (await Promise.all([
                getAppConfig(shortCode),
                new Promise(resolve => setTimeout(resolve, MIN_LOAD_TIME))
            ]))[0]
            set((state) => ({
                ...state,
                shortCode,
                requiresEmail: config?.protection !== 'none' ?? true,
                palette: config?.config?.palette,
                logo: {
                    dark: config?.metadata?.palette?.logo?.dark ?? "",
                    light: config?.metadata?.palette?.logo?.light ?? "",
                },
                i18n: {
                    home: {
                        welcomeText: config?.metadata?.welcome_text ?? "",
                        h1: config?.metadata?.salutation ?? getGreeting(),
                        h2: config?.metadata?.greeting_text ?? "Please choose your assistant.",
                    }
                },
                ready: true,
            }))
        }
        catch (e) {
            console.error(e)
            set(state => ({ ...state, fatal: e.message }))
        }
    },
    resetStore: () => {

        // Remove all custom theme components
        const palette = get().palette
        if (palette?.length) {
            for (const theme in palette) {
                for (const key in palette[theme]) {
                    document.documentElement.style.removeProperty(`--${key.replace("_", "-")}`);
                }
            }
        }

        set(state => ({
            ...state,
            ...INIT,
            requiresEmail: true,
            ready: true
        }))
    },
    loadTheme: (theme) => {

        const palette = get().palette[theme];
        for (const key in palette) {
            document.documentElement.style.setProperty(`--${key.replace("_", "-")}`, palette[key]);
        }

    }

}))

export default useAppConfigStore;