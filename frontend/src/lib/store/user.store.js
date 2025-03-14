import { create } from 'zustand';
import { signUp, validate, login, logout } from '@/lib/api'
import { immer } from 'zustand/middleware/immer';

const INIT = {
    /*
        null :: not yet signed in
        false :: need to sign up
        true :: ready to go
    */
    loggedIn: null,
    userId: null,
    accountId: null,
    email: null,
}

const useUserStore = create(immer((set, get) => ({

    ...INIT,

    validate: async () => {
        const response = await validate();
        const json = await response.json()


        if (response.ok) {
            const { user_id, account_id, email: _email } = json.user;
            set((state) => ({
                ...state,
                userId: user_id || false,
                accountId: account_id || false,
                email: _email || false,
                loggedIn: true,
            }))
        }
        else {
            // Invalid Login
            if (response.status === 401) { //
                set((state) => { state.loggedIn = false })
            }
        }
    },
    signUp: async (shortCode, params, initChatStore) => {
        const response = await signUp(shortCode, params);
        const json = await response.json()

        if (response.ok) {
            const { user_id, account_id, email: _email } = json.user;
            set((state) => ({
                ...state,
                userId: user_id || false,
                accountId: account_id || false,
                email: _email || false,
                loggedIn: true
            }))
            initChatStore()
        }
        else {
            throw new Error(json.detail)
        }
    },
    login: async (params, initChatStore) => {
        const response = await login(params);
        const json = await response.json()

        if (response.ok) {
            const { user_id, account_id, email: _email } = json.user;
            set((state) => ({
                ...state,
                userId: user_id || false,
                accountId: account_id || false,
                email: _email || false,
                loggedIn: true
            }))
            initChatStore()
            
        }
        else {
            throw new Error(json.detail)
        }
    },
    logout: async (resetChatStore) => {

        const response = await logout();
        const json = await response.json()

        if (response.ok) {
            resetChatStore();
            set((state) => ({
                ...state,
                ...INIT,
                loggedIn: false
            }))
        }
        else{
            throw new Error(json.detail)
        }
    },
})))

export default useUserStore;