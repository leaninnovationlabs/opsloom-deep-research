import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "@/components/ui/accordion"
import Markdown from "@/components/Markdown"
import { useId } from "react";
import { cn } from "@/lib/utils";

const AccordionBlock = ({ block, MarkDownProps = {}, className, ...props }) => {
    const { title, content } = block;
    const id = useId();
    return (
        <Accordion type="single" collapsible className={cn("o-w-full", className)}>
            <AccordionItem value={id} className="o-border-none">
                <AccordionTrigger>{title ?? "Explanation"}</AccordionTrigger>
                <AccordionContent>
                    <Markdown {...MarkDownProps}>
                        {content}
                    </Markdown>
                </AccordionContent>
            </AccordionItem>
        </Accordion>
    )
}

export default AccordionBlock