import * as React from "react"

import { cn } from "@/lib/utils"

const Input = React.forwardRef(({ className, type, ...props }, ref) => {
  return (
    (<input
      type={type}
      className={cn(
        "o-flex o-h-9 o-w-full o-rounded-md o-border o-border-input o-bg-transparent o-px-3 o-py-1 o-text-sm o-shadow-sm o-transition-colors file:o-border-0 file:o-bg-transparent file:o-text-sm file:o-font-medium placeholder:o-text-muted-foreground focus-visible:o-outline-none focus-visible:o-ring-1 focus-visible:o-ring-ring disabled:o-cursor-not-allowed disabled:o-opacity-50",
        className
      )}
      ref={ref}
      {...props} />)
  );
})
Input.displayName = "Input"

export { Input }
