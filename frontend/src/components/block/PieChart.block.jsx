import { Pie, PieChart } from "recharts"

import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import {
    ChartContainer,
    ChartTooltip,
    ChartTooltipContent,
} from "@/components/ui/chart"
import { config } from "dotenv"


const chartData = [
    { browser: "chrome", visitors: 275, fill: "var(--color-chrome)" },
    { browser: "safari", visitors: 200, fill: "var(--color-safari)" },
    { browser: "firefox", visitors: 187, fill: "var(--color-firefox)" },
    { browser: "edge", visitors: 173, fill: "var(--color-edge)" },
    { browser: "other", visitors: 90, fill: "var(--color-other)" },
]

const block = { // ?? TODO: Need to work on format 

    data: [
        { browser: "Chrome", visitors: 275},
        { browser: "Safari", visitors: 200},
        { browser: "Firefox", visitors: 187},
        { browser: "Edge", visitors: 173},
        { browser: "Other", visitors: 90 },
    ],
    config: {
        title: "Pie Chart",
        description: "January - June 2024"
    }
}

const chartConfig = {
    visitors: {
        label: "Visitors",
    },
    chrome: {
        label: "Chrome",
        color: "hsl(var(--chart-1))",
    },
    safari: {
        label: "Safari",
        color: "hsl(var(--chart-2))",
    },
    firefox: {
        label: "Firefox",
        color: "hsl(var(--chart-3))",
    },
    edge: {
        label: "Edge",
        color: "hsl(var(--chart-4))",
    },
    other: {
        label: "Other",
        color: "hsl(var(--chart-5))",
    },
}

const PieChartBlock = ({block, ...props}) => {

    // Object.keys(data).reduce((acc, curr) => Object.assign(acc, { [curr]: false }), {})


    return (
        <Card className="o-flex o-flex-col">
            <CardHeader className="o-items-center o-pb-0">
                <CardTitle>Pie Chart</CardTitle>
                <CardDescription>January - June 2024</CardDescription>
            </CardHeader>
            <CardContent className="o-flex-1 o-pb-0">
                <ChartContainer
                    config={chartConfig}
                    className="o-mx-auto o-aspect-square o-max-h-[250px]"
                >
                    <PieChart>
                        <ChartTooltip
                            cursor={false}
                            content={<ChartTooltipContent hideLabel />}
                        />
                        <Pie data={chartData} dataKey="visitors" nameKey="browser" />
                    </PieChart>
                </ChartContainer>
            </CardContent>
            {/* <CardFooter className="flex-col gap-2 text-sm">
                <div className="flex items-center gap-2 font-medium leading-none">
                    Trending up by 5.2% this month <TrendingUp className="h-4 w-4" />
                </div>
                <div className="leading-none text-muted-foreground">
                    Showing total visitors for the last 6 months
                </div>
            </CardFooter> */}
        </Card>
    )
}

export default PieChartBlock;
