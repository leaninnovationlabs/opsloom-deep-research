import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva } from "class-variance-authority";

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "o-inline-flex o-items-center o-justify-center o-whitespace-nowrap o-rounded-md o-text-sm o-font-medium o-transition-colors focus-visible:o-outline-none focus-visible:o-ring-1 focus-visible:o-ring-ring disabled:o-pointer-events-none disabled:o-opacity-50 o-select-none",
  {
    variants: {
      variant: {
        default:
          "o-bg-primary o-text-primary-foreground o-shadow hover:o-bg-primary/90",
        destructive:
          "o-bg-destructive o-text-destructive-foreground o-shadow-sm hover:o-bg-destructive/90",
        outline:
          "o-border o-border-input o-bg-background o-shadow-sm hover:o-bg-accent hover:o-text-accent-foreground",
        secondary:
          "o-bg-secondary o-text-secondary-foreground o-shadow-sm hover:o-bg-secondary/80",
        ghost: "hover:o-bg-accent hover:o-text-accent-foreground",
        link: "o-text-primary o-underline-offset-4 hover:o-underline",
      },
      size: {
        default: "o-h-9 o-px-4 o-py-2",
        sm: "o-h-8 o-rounded-md o-px-3 o-text-xs",
        lg: "o-h-10 o-rounded-md o-px-8",
        icon: "o-h-9 o-w-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

const Button = React.forwardRef(({ className, variant, size, asChild = false, ...props }, ref) => {
  const Comp = asChild ? Slot : "button"
  return (
    (<Comp
      className={cn(buttonVariants({ variant, size, className }))}
      ref={ref}
      {...props} />)
  );
})
Button.displayName = "Button"

export { Button, buttonVariants }
