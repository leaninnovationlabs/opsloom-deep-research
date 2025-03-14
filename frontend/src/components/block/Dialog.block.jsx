
import Card from "@/components/block/Card"
import Markdown from "../Markdown"
import { Button } from "../ui/button"
import { grab } from "@/lib/api"
import { useState } from "react"

// const block = {
//     data: `
// | Month    | Savings |
// | -------- | ------- |
// | January  | $250    |
// | February | $80     |
// | March    | $420    |
//     `,
//     config: {
//         title: "Confirm action", //optional
//         description: "This action will do this", //optional
//         actions: [
//             {
//                 action: "Submit",
//                 url: "https://jsonplaceholder.typicode.com/todos/1",
//                 body: {
//                     "guest_id": 1,
//                     "full_name": "Peter Griffin",
//                     "email": "peter.bigbelly@puffy.com",
//                     "room_type": "single",
//                     "check_in": "2025-06-01T15:00:00",
//                     "check_out": "2025-06-02T11:00:00"
//                 },
//                 method: "POST",
//                 variant: "default" // button type - default || destructive || outline || secondary || ghost || link (see button.jsx)
//             },
//             {
//                 action: "Cancel",
//                 url: null,
//                 variant: "outline"
//             }
//         ]
//     }
// }

const DialogBlock = ({ block, ...props }) => {

    const [loading, setLoading] = useState(false);
    const [done, setDone] = useState(false);

    // Object.keys(data).reduce((acc, curr) => Object.assign(acc, { [curr]: false }), {})
    const { data, config } = block
    const actions = config?.actions ?? []

    return (
        <Card title={config?.title} description={config?.description}>
            <div className="">
                <Markdown>
                    {data}
                </Markdown>
            </div>
            {!done && <div className="o-w-full o-mt-8 o-flex ">
                <div className=" o-flex o-gap-x-4">
                    {
                        actions.map(({ action, url, body, method, variant }, idx) => (
                            <Button key={idx} variant={variant} className="o-max-w-[100px]"
                                disabled={loading}
                                onClick={async () => {
                                    setLoading(true)
                                    try {
                                        if (url) {
                                            await grab(url, method, body);
                                        }
                                        setDone(true)
                                    }
                                    finally {
                                        setLoading(false)
                                    }
                                }}>
                                {action}
                            </Button>
                        ))
                    }
                </div>
            </div>}
        </Card>
    )
}

export default DialogBlock;
