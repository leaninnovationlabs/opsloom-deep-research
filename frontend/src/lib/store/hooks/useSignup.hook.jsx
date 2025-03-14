import { useCallback } from "react";
import useChatStore from "@/lib/store/chat.store";
import useUserStore from "@/lib/store/user.store";
import { useShallow } from "zustand/react/shallow";
import useAppConfigStore from "../appconfig.store";


const useSignup = () => {
    const initChatStore = useChatStore(state => state.initStore)
    const signUpUser = useUserStore(state => state.signUp);
    const shortCode = useAppConfigStore(state => state.shortCode)
    

    const signUp = useCallback(async (params) => {
        await signUpUser(shortCode, params, initChatStore)
    }, [signUpUser, initChatStore])


    return [signUp]
}

export default useSignup;