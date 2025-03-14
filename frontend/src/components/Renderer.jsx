import Table from "@/components/block/Table.block"
import BarChart from "@/components/block/BarChart.block"
import PieChart from "@/components/block/PieChart.block"
import React from "react"
import Markdown from "@/components/Markdown"
import Accordion from "@/components/block/Accordion.block"
import Dialog from "@/components/block/Dialog.block"

// {
//     blocks: [
//         {
//             type: 'text',
//             text: 'Nice, I got a preliminary quote for you. It will be $200 per month. Would you like to proceed?'
//         },
//         {
//             type: 'link',
//             url: 'https://qua.stillwaterinsurance.com/uqp/quote/auto/basic/20PA1111509/dnc',
//             text: 'Click here to proceed'
//         },
//         {
//             type: 'table',
//             data: [
//                 {
//                     vehicle: 'Toyota Corolla',
//                     address: '123 Main Street',
//                     year: 2019,
//                 },{
//                     vehicle: 'Toyota Corolla',
//                     address: '123 Main Street',
//                     year: 2019,
//                 }
//             ],
//             config: {
//                 sortable: true,
//                 filterable: true,
//                 paginated: true,
//                 pageSize: 10
//             }
//         },
//         {
//             type: 'form',
//             data: {
//                 vehicle: 'Toyota Corolla',
//                 address: '123 Main Street',
//                 year: 2019,
//             },
//             template: '<div>{form}</div>',
//             actions: [
//                 {
//                     type: 'submit',
//                     text: 'Submit',
//                     url: 'https://qua.stillwaterinsurance.com/uqp/quote/auto/basic/20PA1111509/dnc'
//                 }
//             ]
//         }
//     ]
// }

const Renderer = ({ children, ...props }) => {

    const blocks = children;

    console.log("BLOCKS", blocks)


    // const tableBlock = {
    //     data: [
    //         { invoice: "INV001", status: "Paid", amount: "$250.00", method: "Credit Card" },
    //         { invoice: "INV002", status: "Pending", amount: "$150.00", method: "PayPal" },
    //         { invoice: "INV003", status: "Unpaid", amount: "$350.00", method: "Bank Transfer" },
    //         { invoice: "INV004", status: "Paid", amount: "$450.00", method: "Credit Card" },
    //         { invoice: "INV005", status: "Paid", amount: "$550.00", method: "PayPal", },
    //         { invoice: "INV006", status: "Pending", amount: "$200.00", method: "Bank Transfer", },
    //         { invoice: "INV007", status: "Unpaid", amount: "$300.00", method: "Credit Card", }
    //     ],
    //     config: {
    //         title: "A list of your recent invoices.",
    //     }
    // }



    // const barChartBlock = {
    //     data: [
    //         { month: "January", desktop: 186 },
    //         { month: "February", desktop: 305 },
    //         { month: "March", desktop: 237 },
    //         { month: "April", desktop: 73 },
    //         { month: "May", desktop: 209 },
    //         { month: "June", desktop: 214 },
    //     ],
    //     config: {
    //         title: "Bar Chart",
    //         description: "January - June 2024",
    //     }
    // }

    return (
        typeof blocks !== "string" ?
            <div>
                {blocks && blocks.map(({ type, ...block }, idx) => (
                    <div key={idx}>


                        {type === "table" &&
                            <Table block={block} />
                        }

                        {type === "barchart" &&
                            <BarChart block={block} />
                        }

                        {type === "piechart" &&
                            <PieChart block={block} />
                        }

                        {type === "accordion" &&
                            <Accordion block={block} />
                        }

                        {type === "dialog" &&
                            <Dialog block={block} />
                        }
                        {type === "text" &&
                            <Markdown>
                                {block.text}
                            </Markdown>
                        }
                    </div>
                ))}


            </div>
            :
            <div className="o-prose dark:o-prose-invert o-break-words">
                <Markdown>
                    {blocks}
                </Markdown>
            </div>
    )
}

export default Renderer