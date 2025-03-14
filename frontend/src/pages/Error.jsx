import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { useId } from "react";

const Error = ({ className, msg, code = 500, ...props }) => {
    const id = useId()
    return (
        <motion.div className={cn("o-w-full o-h-full o-flex o-items-center o-justify-center", className)} key={id} {...props}>
            <div className="o-relative o-h-[25px] o-flex o-flex-row o-gap-4 o-font-light o-items-center">
                <p>
                    {`${code}`}
                </p>
                <div className="o-h-full o-w-[1px] o-bg-foreground" />
                <p className="o-font-sm">
                    {msg}
                </p>
            </div>
        </motion.div>
    )
}

export default Error;