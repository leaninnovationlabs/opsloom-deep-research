import { Card as RadixCard, CardTitle, CardHeader, CardContent, CardFooter, CardDescription } from "@/components/ui/card"
import AccordionBlock from "@/components/block/Accordion.block"

const Card = ({ title, description, explanation, children, ...props }) => {
    return (
        <RadixCard>
            {(title || description) && (
                <CardHeader>
                    {title && <CardTitle>{title}</CardTitle>}
                    {description && <CardDescription>{description}</CardDescription>}
                </CardHeader>
            )}
            <CardContent>
                {children}
            </CardContent>

            {/* Accordion */}
            {(explanation) && (
                <CardFooter>
                    <AccordionBlock block={{
                        title: "Explanation",
                        content: explanation,
                    }}
                        MarkDownProps={{ className: "o-text-sm o-text-muted-foreground" }}
                    />
                </CardFooter>
            )}
        </RadixCard>
    )
}

export default Card;
