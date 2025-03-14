import { useCallback } from "react";
import useChatStore from "@/lib/store/chat.store";
import useUserStore from "@/lib/store/user.store";


const useLogin = () => {
    const initChatStore = useChatStore(state => state.initStore)
    const loginUser = useUserStore(state => state.login);


    const login = useCallback(async (params) => {
        await loginUser(params, initChatStore)
    }, [loginUser, initChatStore])


    return [login]
}

export default useLogin;