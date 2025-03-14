// See: https://fonts.google.com/icons?selected=Material+Symbols+Outlined:search:FILL@0;wght@200;GRAD@0;opsz@20&icon.size=24&icon.color=%23e8eaed&icon.style=Rounded

import { cn } from "@/lib/utils";
import { forwardRef } from "react";

const Icon = forwardRef(({ className, children, ...props }, ref) => {
    return (
        <span className={cn("material-symbols-outlined o-select-none", className)} {...props} ref={ref}>
            {children}
        </span>
    )
})

export default Icon;