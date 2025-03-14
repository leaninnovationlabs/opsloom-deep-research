import useChatStore from '@/lib/store/chat.store'
import { cn, getSessionIdFromLocation } from '@/lib/utils';
import { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useShallow } from 'zustand/react/shallow';
import Avatar from "@/lib/svg/avatar/lil.svg";
import Spinner from "@/lib/svg/spinner/3-dots.svg";
import ThumbsUp from "@/lib/svg/thumbs-up.svg";
import ThumbsDown from "@/lib/svg/thumbs-down.svg";
import { sendFeedback } from '@/lib/api';
import { useState, useLayoutEffect, useRef } from 'react';
import Renderer from '@/components/Renderer';
import Icon from '@/components/Icon';
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";


const Chat = () => {
    const ref = useRef();

    const [messages, loadChat, sessionId, clearChat, isThinking, messageInQueue, sendMessage] = useChatStore(
        useShallow((state) => [state.messages, state.loadChat, state.sessionId, state.clearChat, state.isThinking, state.messageInQueue, state.sendMessage]),
    )

    const location = useLocation();
    const navigate = useNavigate()

    useEffect(() => {
        const newSessionId = getSessionIdFromLocation(location)

        if (!messageInQueue && newSessionId !== sessionId) {
            loadChat(newSessionId)
        }

    }, [location])

    useEffect(() => {
        if (messageInQueue) {
            sendMessage()
        }
    }, [messageInQueue])


    // after we get the sessionId, update the url
    useEffect(() => {
        if (sessionId && sessionId.length) {
            navigate(`/chat/conversation/${sessionId}`, { replace: true })
        }
    }, [sessionId])

    // Clean up state on unmount
    useEffect(() => {
        return () => clearChat();
    }, [])

    useLayoutEffect(() => {
        ref.current.scrollIntoView({ behavior: 'smooth', block: 'end' })
    }, [messages])


    return (
        <div className='o-max-w-2xl o-mx-auto'>

            <div ref={ref} className="o-flex o-flex-col o-pb-[150px] o-mt-2 @sm:o-mt-6 o-p-4 o-gap-y-2">
                {messages.map((message, idx) => (
                    <Message key={idx} message={message} idx={idx} />
                ))}
                {isThinking && <Spinner className="-o-mt-10" />}
            </div>
        </div >
    )
}

import {
    Tooltip,
    TooltipContent,
    TooltipTrigger,
} from "@/components/ui/tooltip";
import { Button } from '@/components/ui/button';

const Message = ({ message, idx }) => {
    const assistant = useChatStore(state => state.assistant)
    const isThinking = useChatStore(state => state.isThinking)
    const shouldReduceMotion = useReducedMotion();

    return (
        <div className={`o-relative o-mb-4 o-group ${message.role === 'user' ? 'o-max-w-[80%] o-ml-auto' : 'o-text-left'}`}>
            {message.role != 'user' && <div className='o-absolute -o-left-16 o-top-2'>
                <AnimatePresence>
                    <motion.div className='o-rounded-xl o-text-primary o-border o-border-foreground/20 o-p-1 o-flex o-items-center o-justify-center'
                        initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                        {!assistant
                            ?
                            <Avatar className="o-w-[25px]  " />
                            :
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Icon className="o-text-md o-cursor-pointer o-text-foreground">
                                        {assistant?.metadata?.icon}
                                    </Icon>
                                </TooltipTrigger>
                                <TooltipContent>
                                    <p>{assistant?.metadata?.title}</p>
                                </TooltipContent>
                            </Tooltip>
                        }
                    </motion.div>
                </AnimatePresence>
            </div>}
            <AnimatePresence>
                <motion.div className={cn("o-inline-block o-p-2 o-rounded-3xl o-w-full", message.role === 'user' ? 'o-bg-muted o-px-6' : "o-mb-2")}
                    initial={{ y: shouldReduceMotion ? 0 : -30, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ x: shouldReduceMotion ? 0 : -30, opacity: 0 }}
                    transition={shouldReduceMotion ? {} : {
                        type: "spring", stiffness: 300, damping: 50,
                        ...(!isThinking && { delay: idx * 0.07 })
                    }}>
                    <Renderer>
                        {message.blocks}
                    </Renderer>


                </motion.div>
            </AnimatePresence>
            {message.sources && (
                <div className="o-mt-2 o-text-sm o-text-gray-500">
                    Sources: {message.sources.map(source => source.source).join(', ')}
                </div>
            )}
            {message.role != 'user' &&
                <Toolbox message={message} className="o-absolute -o-bottom-5 o-left-2" />

            }

        </div>
    )
}

const Toolbox = ({ message, className, style, ...props }) => {
    const isLoading = useChatStore(state => state.isLoading)
    const [feedback, setFeedback] = useState(null);
    useEffect(() => {
        (async () => {
            if ([-1, 0, 1].includes(feedback)) {
                await sendFeedback(message.message_id, feedback)
            }
        })()
    }, [feedback])
    return (
        !isLoading &&
        <div className={cn('o-w-full o-text-primary o-flex o-flex-row group-hover:o-opacity-100 o-opacity-0 o-transition-opacity o-py-1', className)}
            style={{ opacity: feedback ? 1 : "o-revert-layer", ...style }}>
            <button className='o-p-1' onClick={() => setFeedback(x => x === 1 ? 0 : 1)} style={{ opacity: feedback === 1 ? 1 : 0.5 }}>
                <ThumbsUp className="o-size-4" />
            </button>
            <button className='o-p-1' onClick={() => setFeedback(x => x === -1 ? 0 : -1)} style={{ opacity: feedback === -1 ? 1 : 0.5 }}>
                <ThumbsDown className="o-size-4" />
            </button>
        </div>
    )
}

export default Chat 