import * as React from "react"
import * as AccordionPrimitive from "@radix-ui/react-accordion"
import { ChevronDownIcon } from "@radix-ui/react-icons"

import { cn } from "@/lib/utils"

const Accordion = AccordionPrimitive.Root

const AccordionItem = React.forwardRef(({ className, ...props }, ref) => (
  <AccordionPrimitive.Item ref={ref} className={cn("o-border-b", className)} {...props} />
))
AccordionItem.displayName = "AccordionItem"

const AccordionTrigger = React.forwardRef(({ className, children, ...props }, ref) => (
  <AccordionPrimitive.Header className="o-flex">
    <AccordionPrimitive.Trigger
      ref={ref}
      className={cn(
        "o-flex o-flex-1 o-items-center o-justify-between o-py-4 o-text-sm o-font-medium o-transition-all hover:o-underline [&[data-state=open]>svg]:o-rotate-180",
        className
      )}
      {...props}>
      {children}
      <ChevronDownIcon
        className="o-h-4 o-w-4 o-shrink-0 o-text-muted-foreground o-transition-transform o-duration-200" />
    </AccordionPrimitive.Trigger>
  </AccordionPrimitive.Header>
))
AccordionTrigger.displayName = AccordionPrimitive.Trigger.displayName

const AccordionContent = React.forwardRef(({ className, children, ...props }, ref) => (
  <AccordionPrimitive.Content
    ref={ref}
    className="o-overflow-hidden o-text-sm data-[state=closed]:o-animate-accordion-up data-[state=open]:o-animate-accordion-down"
    {...props}>
    <div className={cn("o-pb-4 o-pt-0", className)}>{children}</div>
  </AccordionPrimitive.Content>
))
AccordionContent.displayName = AccordionPrimitive.Content.displayName

export { Accordion, AccordionItem, AccordionTrigger, AccordionContent }
