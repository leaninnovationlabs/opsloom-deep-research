import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm"

const Markdown = ({ className, children, ...props }) => {
    return (
        <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            className={cn("o-prose dark:o-prose-invert o-break-words", className)} {...props}>
            {children}
        </ReactMarkdown>
    )
}

export default Markdown