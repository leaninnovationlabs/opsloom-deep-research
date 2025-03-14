import * as React from "react"
import * as TooltipPrimitive from "@radix-ui/react-tooltip"

import { cn } from "@/lib/utils"

const TooltipProvider = TooltipPrimitive.Provider

const Tooltip = TooltipPrimitive.Root

const TooltipTrigger = TooltipPrimitive.Trigger

const TooltipContent = React.forwardRef(({ className, sideOffset = 4, ...props }, ref) => (
  <TooltipPrimitive.Content
    ref={ref}
    sideOffset={sideOffset}
    className={cn(
      "o-z-50 o-overflow-hidden o-rounded-md o-bg-primary o-px-3 o-py-1.5 o-text-xs o-text-primary-foreground o-animate-in o-fade-in-0 o-zoom-in-95 data-[state=closed]:o-animate-out data-[state=closed]:o-fade-out-0 data-[state=closed]:o-zoom-out-95 data-[side=bottom]:o-slide-in-from-top-2 data-[side=left]:o-slide-in-from-right-2 data-[side=right]:o-slide-in-from-left-2 data-[side=top]:o-slide-in-from-bottom-2",
      className
    )}
    {...props} />
))
TooltipContent.displayName = TooltipPrimitive.Content.displayName

export { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider }
