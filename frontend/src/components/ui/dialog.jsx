import * as React from "react"
import * as DialogPrimitive from "@radix-ui/react-dialog"
import { Cross2Icon } from "@radix-ui/react-icons"

import { cn } from "@/lib/utils"

const Dialog = DialogPrimitive.Root

const DialogTrigger = DialogPrimitive.Trigger

const DialogPortal = DialogPrimitive.Portal

const DialogClose = DialogPrimitive.Close

const DialogOverlay = React.forwardRef(({ className, ...props }, ref) => (
  <DialogPrimitive.Overlay
    ref={ref}
    className={cn(
      "o-fixed o-inset-0 o-z-50 o-bg-black/80  data-[state=open]:o-animate-in data-[state=closed]:o-animate-out data-[state=closed]:o-fade-out-0 data-[state=open]:o-fade-in-0",
      className
    )}
    {...props} />
))
DialogOverlay.displayName = DialogPrimitive.Overlay.displayName

const DialogContent = React.forwardRef(({ className, children, x=true, ...props }, ref) => (
  <DialogPortal>
    <DialogOverlay />
    <DialogPrimitive.Content
      ref={ref}
      className={cn(
        "o-fixed o-left-[50%] o-top-[50%] o-z-50 o-grid o-w-full o-max-w-lg o-translate-x-[-50%] o-translate-y-[-50%] o-gap-4 o-border o-bg-background o-p-6 o-shadow-lg o-duration-200 data-[state=open]:o-animate-in data-[state=closed]:o-animate-out data-[state=closed]:o-fade-out-0 data-[state=open]:o-fade-in-0 data-[state=closed]:o-zoom-out-95 data-[state=open]:o-zoom-in-95 data-[state=closed]:o-slide-out-to-left-1/2 data-[state=closed]:o-slide-out-to-top-[48%] data-[state=open]:o-slide-in-from-left-1/2 data-[state=open]:o-slide-in-from-top-[48%] @sm:o-rounded-lg",
        className
      )}
      {...props}>
      {children}
      {x && <DialogPrimitive.Close
        className="o-absolute o-right-4 o-top-4 o-rounded-sm o-opacity-70 o-ring-offset-background o-transition-opacity hover:o-opacity-100 focus:o-outline-none focus:o-ring-2 focus:o-ring-ring focus:o-ring-offset-2 disabled:o-pointer-events-none data-[state=open]:o-bg-accent data-[state=open]:o-text-muted-foreground">
        <Cross2Icon className="o-h-4 o-w-4" />
        <span className="o-sr-only">Close</span>
      </DialogPrimitive.Close>}
    </DialogPrimitive.Content>
  </DialogPortal>
))
DialogContent.displayName = DialogPrimitive.Content.displayName

const DialogHeader = ({
  className,
  ...props
}) => (
  <div
    className={cn("o-flex o-flex-col o-space-y-1.5 o-text-center @sm:o-text-left", className)}
    {...props} />
)
DialogHeader.displayName = "DialogHeader"

const DialogFooter = ({
  className,
  ...props
}) => (
  <div
    className={cn("o-flex o-flex-col-reverse @sm:o-flex-row @sm:o-justify-end @sm:o-space-x-2", className)}
    {...props} />
)
DialogFooter.displayName = "DialogFooter"

const DialogTitle = React.forwardRef(({ className, ...props }, ref) => (
  <DialogPrimitive.Title
    ref={ref}
    className={cn("o-text-lg o-font-semibold o-leading-none o-tracking-tight", className)}
    {...props} />
))
DialogTitle.displayName = DialogPrimitive.Title.displayName

const DialogDescription = React.forwardRef(({ className, ...props }, ref) => (
  <DialogPrimitive.Description
    ref={ref}
    className={cn("o-text-sm o-text-muted-foreground", className)}
    {...props} />
))
DialogDescription.displayName = DialogPrimitive.Description.displayName

export {
  Dialog,
  DialogPortal,
  DialogOverlay,
  DialogTrigger,
  DialogClose,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
}
