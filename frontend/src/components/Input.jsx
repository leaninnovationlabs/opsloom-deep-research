import React from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import useChatStore from '@/lib/store/chat.store'
import { cn, isNewChatLocation } from '@/lib/utils'
import { useLocation, useNavigate } from 'react-router-dom'
import { useShallow } from 'zustand/react/shallow'
import PoweredBy from './PoweredBy'
import Icon from './Icon'
import { useMemo } from 'react'


const MessageInput = ({ className, ...props }) => {
    const [input, setInput, queueMessage, isLoading] = useChatStore(
        useShallow((state) => [state.input, state.setInput, state.queueMessage, state.isLoading]),
    )

    const location = useLocation();
    const navigate = useNavigate();


    const handleSubmit = async (e) => {
        e.preventDefault()
        queueMessage();
        if (isNewChatLocation(location)) {
            navigate("/chat");
        }
    }

    const disabled = useMemo(() => isLoading || !(input?.length && input.length > 0), [isLoading, input])

    return (
        <div className=' o-grid o-grid-rows-[1fr_24px]'>

            <form onSubmit={handleSubmit} className={cn("o-relative o-w-full", className)} {...props}>
                <Input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask a question..."
                    className="o-bg-background dark:o-bg-muted o-border o-border-primary/15 o-h-12 o-rounded-3xl o-pl-5 o-pr-[72px]"
                />
                <div className='o-h-full o-w-fit o-absolute o-right-4 o-top-0 o-flex o-items-center o-flex-row o-gap-x-[6px]'>
                    <button type="button" className='o-h-full o-flex o-items-center'>
                        <Icon className="o-pointer-events-none">
                            mic
                        </Icon>
                    </button>
                    <button type="submit" disabled={disabled} className={cn(
                        'o-rounded-full o-border o-border-foreground/50 o-h-6 o-w-6 o-flex o-items-center o-justify-center o-transition-all',
                        disabled ? "o-opacity-50" : "hover:o-border-foreground"
                    )}>
                        <Icon className="o-pointer-events-none">
                            arrow_upward
                        </Icon>
                    </button>
                </div>
            </form>
            <div className='o-w-full o-flex o-justify-center o-items-center @sm:o-hidden'>
                <PoweredBy />
            </div>
        </div>
    )
}

export default MessageInput