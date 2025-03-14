
import Opsloom from "@/lib/svg/logo.svg"
import { cn } from "@/lib/utils"
import { memo } from "react"

const PoweredBy = memo(({className, ...props}) => (
    <div className={cn('o-flex o-flex-row o-items-end w-fit', className)} {...props}>
        <p className='o-text-[11px] o-opacity-25 o-pr-1 o-mb-[1px]'>
            Powered by
        </p>
        <Opsloom className="o-h-[16px] o-w-fit o-opacity-30" />
    </div>
))

export default PoweredBy