import { TooltipProvider as RadixTooltipProvider } from "@/components/ui/tooltip"


export const TooltipProvider = ({ children, ...props }) => {
    return (
        <RadixTooltipProvider delayDuration={0} {...props}>
            {children}
        </RadixTooltipProvider>
    )

}
