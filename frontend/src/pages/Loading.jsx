import Spinner from "@/lib/svg/spinner/ring.svg";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { useId } from "react";

const Loading = ({ className, ...props }) => {
    const id = useId()
    return (
        <motion.div className={cn("o-w-full o-h-full o-flex o-items-center o-justify-center", className)} key={id} {...props}>
            <Spinner />
        </motion.div>
    )
}

export default Loading;