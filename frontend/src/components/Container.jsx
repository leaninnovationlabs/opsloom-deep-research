// The little chat icon that expands/collapses the whole app only in widget mode. Else just renders full page app

import { MODE, MODE_TYPES } from "@/lib/constants";
import { cn } from "@/lib/utils";
import { AnimatePresence, motion } from "framer-motion";
import { useState } from "react";


const Container = ({ children, ...props }) => {
    const [expanded, setExpanded] = useState(false)

    return (
        <>
            {MODE === MODE_TYPES.BUBBLE_WIDGET ?
                <div className="o-@container o-w-[405px] o-h-[708px] o-mr-12 o-mb-12 o-fixed o-bottom-0 o-right-0 o-bg-background">
                    <div className='o-cursor-pointer o-absolute o-z-50 -o-bottom-8 -o-right-8 o-rounded-full o-w-[50px] o-h-[50px] o-bg-foreground o-text-background o-flex o-justify-center o-items-center' onClick={() => setExpanded(x => !x)}>
                        <AnimatePresence mode="sync">

                            {!expanded ?
                                <motion.div key="msg" className="o-flex o-items-center o-justify-center o-absolute o-bottom-0 o-to-0 o-w-full o-h-full" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.3 }}>
                                    <svg width="22" height="22" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path fillRule="evenodd" clipRule="evenodd" d="M17.5433 3.7039C18 4.80653 18 6.20435 18 9C18 11.7956 18 13.1935 17.5433 14.2961C16.9343 15.7663 15.7663 16.9343 14.2961 17.5433C13.1935 18 11.7956 18 9 18H6C3.17157 18 1.75736 18 0.87868 17.1213C0 16.2426 0 14.8284 0 12V9C0 6.20435 0 4.80653 0.456723 3.7039C1.06569 2.23373 2.23373 1.06569 3.7039 0.456723C4.80653 0 6.20435 0 9 0C11.7956 0 13.1935 0 14.2961 0.456723C15.7663 1.06569 16.9343 2.23373 17.5433 3.7039ZM5 6.99966C5 6.44738 5.44772 5.99966 6 5.99966H12C12.5523 5.99966 13 6.44738 13 6.99966C13 7.55195 12.5523 7.99966 12 7.99966H6C5.44772 7.99966 5 7.55195 5 6.99966ZM5 10.9997C5 10.4474 5.44772 9.99966 6 9.99966H9C9.55228 9.99966 10 10.4474 10 10.9997C10 11.5519 9.55228 11.9997 9 11.9997H6C5.44772 11.9997 5 11.5519 5 10.9997Z" fill="currentColor" />
                                    </svg>

                                </motion.div>
                                :
                                <motion.div key="x" className="o-flex o-items-center o-justify-center o-absolute o-bottom-0 o-to-0 o-w-full o-h-full" initial={{ opacity: 0, rotate: "-365deg", scale: 0 }} animate={{ opacity: 1, rotate: "0deg", scale: 1 }} exit={{ opacity: 0, transition: { duration: 0.2 } }} transition={{ duration: 0.5 }}>
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M18 6L6 18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                                        <path d="M6 6L18 18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>

                                </motion.div>
                            }

                        </AnimatePresence>
                    </div>

                    <div className="o-absolute o-w-full o-h-full o-overflow-hidden o-z-0">
                        <motion.div animate={{ y: expanded ? 0 : "100%", opacity: expanded ? 1 : 0 }} className="o-absolute o-bottom-0 o-right-0 o-w-full o-h-full o-overflow-hidden o-rounded-lg" transition={{ type: "spring", stiffness: 400, damping: 50, restDelta: 0.005 }}>
                            {children}
                        </motion.div>
                    </div>
                </div>
                :
                <div className={cn("o-@container o-bg-background", MODE === MODE_TYPES.FILL_PARENT ? "o-h-full o-w-full" : "o-w-screen o-h-screen")}>
                    {children}
                </div>
            }
        </>


    )
}

export default Container;