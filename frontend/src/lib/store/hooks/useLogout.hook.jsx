import { useCallback, useMemo } from "react";
import useAppConfigStore from "@/lib/store/appconfig.store";
import useChatStore from "@/lib/store/chat.store";
import useUserStore from "@/lib/store/user.store";
import { useShallow } from "zustand/react/shallow";
import { useNavigate } from "react-router-dom";
import { MODE, MODE_TYPES } from "@/lib/constants";


const useLogout = () => {
    const navigate = useNavigate();
    const requiresEmail = useAppConfigStore(state =>  state.requiresEmail);
    const resetChatStore = useChatStore(state => state.resetStore)
    const [logoutUser, loggedIn] = useUserStore(useShallow(state => [state.logout, state.loggedIn]));


    const logout = useCallback(async () => {
        navigate("/")
        await logoutUser(resetChatStore);
    }, [logoutUser, resetChatStore])


    const showLogout = useMemo(() => requiresEmail && loggedIn && MODE === MODE_TYPES.WEBAPP, [requiresEmail, loggedIn])

    return [logout, showLogout, MODE]
}

export default useLogout;