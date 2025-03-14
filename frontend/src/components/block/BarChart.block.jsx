import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts"
import {
    ChartContainer,
    ChartTooltip,
    ChartTooltipContent,
} from "@/components/ui/chart"
import Card from "@/components/block/Card"

const BarChartBlock = ({ block, ...children }) => {
    const { data, config } = block;

    return (
        <Card
            title={config?.title}
            description={config?.description}
            explanation={config?.explanation}
        >
            <ChartContainer config={{}}>
                <BarChart accessibilityLayer data={data}>
                    <CartesianGrid vertical={false} />
                    <XAxis
                        dataKey={config?.xAxis ?? ""}
                        tickLine={false}
                        tickMargin={10}
                        axisLine={false}
                        tickFormatter={(value) => value.slice(0, 10)}
                    />
                    <YAxis
                        dataKey={config?.yAxis ?? ""}
                        tickLine={false}
                        tickMargin={10}
                        axisLine={false}
                    />
                    <ChartTooltip
                        cursor={false}
                        content={<ChartTooltipContent hideLabel />}
                    />
                    <Bar dataKey={config?.yAxis ?? ""} fill="hsl(var(--chart-1))" radius={8} />
                </BarChart>
            </ChartContainer>
        </Card>
    )
}

export default BarChartBlock
