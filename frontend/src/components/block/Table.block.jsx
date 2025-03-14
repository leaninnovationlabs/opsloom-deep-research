import {
    Table,
    TableBody,
    TableCaption,
    TableCell,
    TableFooter,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { cn } from "@/lib/utils"
import Card from "@/components/block/Card"

/*
const block = {
    data: [
        { invoice: "INV001", status: "Paid", amount: "$250.00", method: "Credit Card" },
        { invoice: "INV002", status: "Pending", amount: "$150.00", method: "PayPal" },
        { invoice: "INV003", status: "Unpaid", amount: "$350.00", method: "Bank Transfer" },
        { invoice: "INV004", status: "Paid", amount: "$450.00", method: "Credit Card" },
        { invoice: "INV005", status: "Paid", amount: "$550.00", method: "PayPal", },
        { invoice: "INV006", status: "Pending", amount: "$200.00", method: "Bank Transfer", },
        { invoice: "INV007", status: "Unpaid", amount: "$300.00", method: "Credit Card", }
    ],
    config: {
        title: "A list of your recent invoices.",
    }
}
*/

const TableBlock = ({ block, ...props }) => {
    const { data, config } = block
    return (
        <Card title={config?.title} description={config?.description}>
            <Table className="o-w-full">
                {data && data.length && <TableHeader>
                    <TableRow>
                        {Object.keys(data[0]).map((col, idx, arr) => (
                            <TableHead className={cn("capitalize", arr.length - 1 === idx && arr.length !== 1 && "o-text-right")} key={idx}>
                                {col}
                            </TableHead>
                        ))}
                    </TableRow>
                </TableHeader>}
                {data && data.length && <TableBody>
                    {data.map((cols, idx) => (
                        <TableRow key={idx}>
                            {Object.keys(cols).map((col, idy, arr) => (
                                <TableCell className={cn(arr.length - 1 === idy && arr.length !== 1 && "o-text-right")} key={idy}>
                                    {cols[col]}
                                </TableCell>
                            ))}
                        </TableRow>
                    ))}
                </TableBody>}
            </Table>
        </Card>
    )
}

export default TableBlock;