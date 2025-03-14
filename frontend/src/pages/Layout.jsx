import MessageInput from "@/components/Input"
import Nav, { HeadlessNav } from "@/components/Nav"
import Dialog from "@/components/Dialog"
import { useLocation } from "react-router-dom"
import { HEADLESS } from "@/lib/constants"
import { cn } from "@/lib/utils"

const Layout = ({ children }) => {
    const location = useLocation();

    return (
        <>
            <Dialog.Welcome />
            <div className="o-bg-muted/20 dark:o-bg-muted/50 o-h-full">

                {!HEADLESS && <Nav />}
                {HEADLESS && <HeadlessNav />}
                <main className={cn("o-absolute o-overflow-y-auto o-w-full o-h-full o-pt-[60px]", !HEADLESS && "@sm:o-pl-[320px]")}>
                    {children}
                </main>

                {location.pathname !== "/" && <div className={cn("o-absolute o-bottom-0 o-left-0 o-w-full o-pointer-events-none", !HEADLESS && "@sm:o-pl-[320px]")}>
                    <div className="o-max-w-2xl o-mx-auto o-px-4">
                        <MessageInput className="o-w-full o-pointer-events-auto" />
                    </div>

                </div>}
            </div>
        </>

    )
}

export default Layout