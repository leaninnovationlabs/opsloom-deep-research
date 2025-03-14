import { Button } from "@/components/ui/button"
import useChatStore from "@/lib/store/chat.store"
import Opsloom from "@/lib/svg/logo.svg"
import { cn, getSessionIdFromLocation, transition } from "@/lib/utils"
import { useState, useEffect } from "react"
import { motion, AnimatePresence, useReducedMotion } from "framer-motion"
import { Link, useLocation, useNavigate } from "react-router-dom"
import MessageIcon from "@/lib/svg/message.svg"
import PlusIcon from "@/lib/svg/plus.svg"
import Icon from "./Icon"
import { useShallow } from "zustand/react/shallow"
import useAppConfigStore from "@/lib/store/appconfig.store"
import Toolbar from "@/components/Toolbar";
import PoweredBy from "./PoweredBy"

const Nav = ({ children, ...props }) => {
    const [history, refreshHistory, refreshHomeScreen] = useChatStore(
        useShallow(state => [state.history, state.refreshHistory, state.refreshHomeScreen])
    )
    const logo = useAppConfigStore(state => state.logo);

    const shouldReduceMotion = useReducedMotion();

    const location = useLocation();

    const [currSession, setCurrSession] = useState()

    useEffect(() => {
        setCurrSession(getSessionIdFromLocation(location))
        if (location.pathname !== "/") {
            refreshHistory()
        }
    }, [location])

    const [mobileMenu, showMobileMenu] = useState(false);

    const History =
        <AnimatePresence mode="popLayout">
            {[...history].sort((a, b) => (new Date(b.created_at)) - (new Date(a.created_at))).map(({ created_at, id, title }, idx, arr) => (
                <motion.div key={id} layout="preserve-aspect"  {...transition(0.2 * idx, shouldReduceMotion)}>
                    <Link className={cn("o-relative o-px-2 o-py-[6px] o-w-full o-group hover:o-bg-muted o-rounded-lg o-grid o-grid-cols-[auto_1fr] o-gap-x-2 o-items-center", currSession === id && "o-bg-muted")} to={`/chat/conversation/${id}`} onClick={() => showMobileMenu(false)}>
                        <MessageIcon className="o-size-4 o-text-foreground/50" />
                        <AnimatePresence mode="wait">
                            {title ?
                                <motion.p key="with-title" className="o-whitespace-nowrap o-overflow-x-hidden o-text-sm" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                                    {title}
                                </motion.p>
                                :
                                <motion.p key="without-title" className="o-whitespace-nowrap o-overflow-x-hidden o-text-sm" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                                    New Chat
                                </motion.p>
                            }
                        </AnimatePresence>
                        {/* Cool Overflow Gradient */}
                        {currSession === id ? <div className="o-absolute o-w-[40px] o-h-full o-right-2 o-top-0 o-bg-gradient-to-r o-from-transparent o-to-muted o-rounded-r-lg" /> :
                            <div className="o-absolute o-w-[40px] o-h-full o-right-2 o-top-0 o-bg-gradient-to-r o-from-transparent group-hover:o-to-muted o-to-background o-rounded-r-lg" />}
                    </Link>
                </motion.div>

            ))}
        </AnimatePresence>


    const Logo =
        <Link to="/" onClick={() => showMobileMenu(false)}>
            <>
                {
                    !logo?.dark ? <Opsloom className="o-w-[90px] o-mt-[2px]" />
                        :
                        <div className="[&>*]:o-h-full [&>*]:o-max-w-[130px]">
                            <img className="o-hidden dark:o-block" src={logo.dark} alt="logo" />
                            <img className="dark:o-hidden" src={logo.light} alt="logo" />
                        </div>
                }
            </>

        </Link>


    return (
        <>
            <Toolbar className="o-hidden sm:o-block o-pl-[320px]" />
            <nav className="o-z-[49] o-fixed o-w-[320px] o-h-full o-bg-background o-hidden @sm:o-block o-border-r ">
                <div className="o-relative o-w-full o-h-full  ">

                    <div className="o-grid o-grid-cols-[auto_1fr] o-gap-6 o-px-6 o-py-5 o-items-center o-border-b">


                        {Logo}


                        <Link to="/" >
                            <Button variant="outline" className="o-w-full o-justify-center o-h-10 o-bg-muted/50"
                                onClick={() => {
                                    if (location.pathname === "/") refreshHomeScreen()
                                }}>
                                <PlusIcon className="o-size-4 -o-translate-x-2 o-stroke-2" />
                                New Chat
                            </Button>
                        </Link>
                    </div>

                    <motion.div layout layoutRoot className="o-relative o-flex o-flex-col o-px-2 o-overflow-y-auto o-h-[calc(100%-81px)] o-w-full o-p-4 o-pb-8 o-mt-[1px] o-select-none">
                        {History}
                    </motion.div>

                    <div className="o-absolute o-bottom-0 o-left-0 o-w-full o-h-full o-flex o-items-end o-justify-center o-p-4 o-pointer-events-none">
                        <PoweredBy />
                    </div>


                </div>
            </nav>


            {/* Mobile Stuff */}
            <div className="@sm:o-hidden" />
            <nav className="@sm:o-hidden o-absolute o-top-0 o-left-0 o-z-10 o-bg-background o-w-full o-h-[60px] o-grid o-grid-cols-[auto_1fr] o-items-center o-px-4">
                {Logo}
                <Icon className="o-text-4xl o-justify-self-end o-cursor-pointer o-select-none" onClick={() => showMobileMenu(x => !x)}>
                    {mobileMenu ? "close" : "menu"}
                </Icon>
            </nav>
            <AnimatePresence>
                {mobileMenu &&
                    <motion.menu key="mobile-menu" className="@sm:o-hidden o-bg-background o-w-full o-h-full o-absolute o-top-0 o-left-0 o-z-50 o-p-4 o-pt-[72px] o-overflow-y-auto"
                        animate={{ y: 60 }} initial={{ y: "100%" }} exit={{ y: "100%", transition: { type: "spring", stiffness: 200, damping: 20 } }}
                        transition={{ type: "spring", stiffness: 100, damping: 20 }}>
                        <Toolbar className="o-border-t o-px-4 o-h-[55px]" closeMobileMenu={() => showMobileMenu(false)} />

                        <Link to="/" onClick={() => showMobileMenu(false)}>
                            <Button variant="outline" className="o-w-full o-justify-start o-h-10 o-bg-muted/50 o-mb-6">
                                <PlusIcon className="o-size-4 -o-translate-x-2 o-stroke-2" />
                                New Chat
                            </Button>
                        </Link>
                        {History}
                    </motion.menu>
                }
            </AnimatePresence>
        </>
    )
}

export const HeadlessNav = () => {
    const navigate = useNavigate();
    const location = useLocation();
    return (
        <AnimatePresence initial="false">
            {location.pathname !== "/" && <motion.div key="back-btn" className="o-fixed o-z-10 o-top-0 o-left-0 o-w-full o-h-[60px] o-border-b o-backdrop-blur-[10px]" {...transition(0, true)}>
                <div className="o-h-full o-w-fit o-flex o-items-center o-justify-center o-px-4 o-cursor-pointer" onClick={() => navigate(-1)}>
                    <Icon className="!o-text-[40px]">
                        arrow_back
                    </Icon>
                </div>
            </motion.div>}
        </AnimatePresence>
    )
}

export default Nav