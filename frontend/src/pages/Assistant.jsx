import Icon from "@/components/Icon"
import useChatStore from "@/lib/store/chat.store"
import { transition } from "@/lib/utils"
import { AnimatePresence, motion, useReducedMotion } from "framer-motion"
import { useEffect } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { useShallow } from "zustand/react/shallow"

const Assistant = (props) => {
    const [setInput, setAssistant, assistants, assistant, queueMessage] = useChatStore(
        useShallow((state) => [state.setInput, state.setAssistant, state.assistants, state.assistant, state.queueMessage]),
    )

    const navigate = useNavigate()
    const location = useLocation();
    const shouldReduceMotion = useReducedMotion();

    // Change target assistant everytime this page loads
    useEffect(() => {
        setAssistant(location.pathname.split("/").at(-1))
    }, [assistants])

    const metadata = assistant?.metadata

    const handleClickPrompt = (prompt) => {
        // TODO: could create race condition 
        setInput(prompt)
        queueMessage()
        navigate("/chat");
    }


    return (
        <div className="o-max-w-2xl o-w-fit o-h-full o-mx-auto o-px-4 o-pb-12 o-grid o-grid-rows-[1fr_auto]">
            <AnimatePresence>


                <motion.div className="o-w-full o-flex o-justify-center" key="title" {...transition(0, shouldReduceMotion)}>
                    <div className="@lg:o-mb-[10vh] o-flex o-flex-row o-gap-4 o-items-center">
                        <Icon className="!o-text-[60px]">
                            {metadata?.icon}
                        </Icon>
                        <div>
                            <h2 className="o-text-5xl o-leading-[1.1] o-font-medium o-mb-1">
                                {metadata?.title}
                            </h2>
                            <p className="o-text-muted-foreground o-pl-2">
                                {metadata?.description}
                            </p>
                        </div>
                    </div>
                </motion.div>
                <motion.div className="o-grid @lg:o-grid-cols-2 o-gap-4 o-mb-16 o-w-full" key="prompts" {...transition(2, shouldReduceMotion)}>

                    {
                        metadata?.prompts?.map((prompt, idx) => (
                            <div onClick={() => handleClickPrompt(prompt)} key={idx}
                                className="o-text-sm o-text-muted-foreground o-bg-transparent o-w-full o-h-full o-border o-rounded-lg o-p-5 o-flex o-flex-col o-gap-2 o-leading-snug o-select-none o-group hover:o-bg-muted o-transition-colors o-line-clamp-2">
                                {prompt}
                            </div>

                        ))
                    }
                </motion.div>
            </AnimatePresence>
        </div>
    )
}

export default Assistant