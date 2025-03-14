import * as React from "react"
import * as SheetPrimitive from "@radix-ui/react-dialog"
import { Cross2Icon } from "@radix-ui/react-icons"
import { cva } from "class-variance-authority";

import { cn } from "@/lib/utils"

const Sheet = SheetPrimitive.Root

const SheetTrigger = SheetPrimitive.Trigger

const SheetClose = SheetPrimitive.Close

const SheetPortal = SheetPrimitive.Portal

const SheetOverlay = React.forwardRef(({ className, ...props }, ref) => (
  <SheetPrimitive.Overlay
    className={cn(
      "o-fixed o-inset-0 o-z-50 o-bg-black/80 o- data-[state=open]:o-animate-in data-[state=closed]:o-animate-out data-[state=closed]:o-fade-out-0 data-[state=open]:o-fade-in-0",
      className
    )}
    {...props}
    ref={ref} />
))
SheetOverlay.displayName = SheetPrimitive.Overlay.displayName

const sheetVariants = cva(
  "o-fixed o-z-50 o-gap-4 o-bg-background o-p-6 o-shadow-lg o-transition o-ease-in-out data-[state=closed]:o-duration-300 data-[state=open]:o-duration-500 data-[state=open]:o-animate-in data-[state=closed]:o-animate-out",
  {
    variants: {
      side: {
        top: "o-inset-x-0 o-top-0 o-border-b data-[state=closed]:o-slide-out-to-top data-[state=open]:o-slide-in-from-top",
        bottom:
          "o-inset-x-0 o-bottom-0 o-border-t data-[state=closed]:o-slide-out-to-bottom data-[state=open]:o-slide-in-from-bottom",
        left: "o-inset-y-0 o-left-0 o-h-full o-border-r data-[state=closed]:o-slide-out-to-left data-[state=open]:o-slide-in-from-left o-max-w-sm",
        right:
          "o-inset-y-0 o-right-0 o-h-full o-border-l data-[state=closed]:o-slide-out-to-right data-[state=open]:o-slide-in-from-right o-max-w-sm",
      },
    },
    defaultVariants: {
      side: "right",
    },
  }
)

const SheetContent = React.forwardRef(({ side = "right", className, children, ...props }, ref) => (
  <SheetPortal>
    <SheetOverlay />
    <SheetPrimitive.Content ref={ref} className={cn(sheetVariants({ side }), className)} {...props}>
      <SheetPrimitive.Close
        className="o-absolute o-right-6 o-top-6 o-rounded-sm o-opacity-70 o-ring-offset-background o-transition-opacity hover:o-opacity-100 focus:o-outline-none focus:o-ring-2 focus:o-ring-ring focus:o-ring-offset-2 disabled:o-pointer-events-none data-[state=open]:o-bg-secondary">
        <Cross2Icon className="o-h-4 o-w-4" />
        <span className="o-sr-only">Close</span>
      </SheetPrimitive.Close>
      {children}
    </SheetPrimitive.Content>
  </SheetPortal>
))
SheetContent.displayName = SheetPrimitive.Content.displayName

const SheetHeader = ({
  className,
  ...props
}) => (
  <div
    className={cn("o-flex o-flex-col o-space-y-2 o-text-left", className)}
    {...props} />
)
SheetHeader.displayName = "SheetHeader"

const SheetFooter = ({
  className,
  ...props
}) => (
  <div
    className={cn(
      "o-flex o-flex-col-reverse @sm:o-flex-row @sm:o-justify-end @sm:o-space-x-2",
      className
    )}
    {...props} />
)
SheetFooter.displayName = "SheetFooter"

const SheetTitle = React.forwardRef(({ className, ...props }, ref) => (
  <SheetPrimitive.Title
    ref={ref}
    className={cn("o-text-lg o-font-semibold o-text-foreground", className)}
    {...props} />
))
SheetTitle.displayName = SheetPrimitive.Title.displayName

const SheetDescription = React.forwardRef(({ className, ...props }, ref) => (
  <SheetPrimitive.Description
    ref={ref}
    className={cn("o-text-sm o-text-muted-foreground", className)}
    {...props} />
))
SheetDescription.displayName = SheetPrimitive.Description.displayName

export {
  Sheet,
  SheetPortal,
  SheetOverlay,
  SheetTrigger,
  SheetClose,
  SheetContent,
  SheetHeader,
  SheetFooter,
  SheetTitle,
  SheetDescription,
}
