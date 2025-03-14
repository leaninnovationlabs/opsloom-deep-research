import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
    Sheet,
    SheetClose,
    SheetContent,
    SheetDescription,
    SheetFooter,
    SheetHeader,
    SheetTitle,
    SheetTrigger,
} from "@/components/ui/sheet"

import Icon from '@/components/Icon';
import useChatStore from "@/lib/store/chat.store";
import { cn, transition } from "@/lib/utils";
import { useLocation, useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import useLogout from "@/lib/store/hooks/useLogout.hook";

const Toolbar = ({ className, closeMobileMenu = () => { }, ...props }) => {
    const assistant = useChatStore(state => state.assistant)
    const location = useLocation();
    const navigate = useNavigate();
    const [logout, showLogout] = useLogout()

    return (


        <nav className={cn('o-absolute o-top-0 o-left-0 o-border-b o-w-full o-z-1 @sm:o-z-[48] o-bg-background @xl:o-backdrop-blur-[10px] dark:@xl:o-bg-transparent o-h-[64px]',
            (location.pathname === "/" || location.pathname.includes("assistant")) && "o-bg-transparent @sm:o-border-b-[0px]", className)} {...props}>

            <div className="o-flex o-flex-row o-h-full o-w-full o-px-1 @sm:o-px-8 o-items-center">
                <AnimatePresence mode="wait">
                    {location.pathname.includes("/chat") && assistant?.id && <motion.div key={assistant?.id} className='o-h-fit'  {...transition(0, true)}>

                        <Sheet>
                            <DropdownMenu modal={false}>
                                <DropdownMenuTrigger asChild>
                                    <div className="o-flex o-flex-row o-items-center o-gap-x-2 o-select-none o-cursor-pointer">
                                        <Icon>
                                            {assistant?.metadata?.icon}
                                        </Icon>
                                        <p className="o-text-sm">{assistant?.metadata?.title} </p>
                                        <Icon>keyboard_arrow_down</Icon>
                                    </div>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent className="o-w-56">
                                    {/* <DropdownMenuLabel>Assistant Options</DropdownMenuLabel>
                                <DropdownMenuSeparator /> */}
                                    <DropdownMenuItem>
                                        <SheetTrigger className="o-flex o-w-full">
                                            <Icon>info</Icon><p className="o-pl-2">Quick View</p>
                                        </SheetTrigger>
                                    </DropdownMenuItem>

                                    {/* <DropdownMenuItem><Icon>brush</Icon>Customize</DropdownMenuItem>
                            <DropdownMenuSeparator /> */}
                                    {/* <DropdownMenuItem><Icon>forum</Icon>Leave Feedback</DropdownMenuItem> */}
                                    <DropdownMenuSeparator />
                                    <DropdownMenuItem onClick={() => {
                                        navigate(`/assistant/${assistant?.id}`);
                                        closeMobileMenu()
                                    }}>
                                        <Icon>arrow_circle_right</Icon>
                                        Launch Assistant
                                    </DropdownMenuItem>

                                </DropdownMenuContent>
                            </DropdownMenu>

                            <SheetContent className="o-p-0 o-pt-5" >
                                <SheetHeader>
                                    <SheetTitle className="o-flex o-items-center o-gap-x-1 o-px-6"><Icon>info</Icon><p>Assistant Info</p></SheetTitle>
                                    <SheetDescription className="o-overflow-auto o-h-[calc(100vh-62px)] o-px-6"> TODO: remove vh

                                        Lorem ipsum odor amet, consectetuer adipiscing elit. Id sed consectetur tempus nullam lobortis fringilla. Sapien blandit commodo per libero blandit hendrerit egestas lacus. Luctus nunc eleifend curabitur volutpat inceptos libero lobortis vestibulum. Nec tellus fames malesuada porta posuere fusce; tempor pulvinar. Consectetur aliquet scelerisque sem tortor primis placerat. Habitant integer per dolor primis mattis curabitur interdum dolor. Justo maecenas auctor magna class velit montes egestas.<br />

                                        Dapibus eu amet amet nostra nec; erat consequat. Nisi sit dapibus molestie purus arcu. Ipsum tincidunt rutrum commodo; penatibus volutpat purus hendrerit morbi. Primis porttitor massa molestie fringilla risus montes. Adipiscing convallis volutpat parturient elementum porta congue arcu. Primis lacinia morbi nisi odio nibh sollicitudin orci. Maecenas purus efficitur sit penatibus nullam viverra ante fusce. Proin congue senectus parturient lectus adipiscing sem porttitor rutrum? Vel rhoncus posuere aliquet consequat nibh ex. Ligula himenaeos pretium blandit placerat phasellus.<br />

                                        Ultrices eros nisi himenaeos quisque, hac odio himenaeos. Nisl vivamus fames ut sodales ut, parturient penatibus curabitur. Bibendum enim inceptos bibendum malesuada, tristique pretium semper. Maecenas ridiculus pulvinar per augue natoque blandit. Orci tincidunt litora lorem; class leo efficitur urna himenaeos. Erat ipsum condimentum amet platea accumsan himenaeos. Luctus facilisi efficitur justo auctor duis netus dictum. Ac arcu libero id ornare eu ad cubilia. Suscipit quis suspendisse vehicula arcu nam aenean quam.<br />

                                        Ligula quis scelerisque posuere neque in arcu. Fusce consequat nunc facilisi phasellus vel hac ut dictumst ac. Himenaeos curabitur facilisis fusce et class donec dictumst consequat. Primis dignissim nullam dapibus eget imperdiet commodo. Dis id donec elit conubia magna. Vestibulum primis nullam tempor in vestibulum finibus justo. Phasellus quam rutrum malesuada inceptos montes tempor leo et nascetur.

                                        Sapien tortor eget hac sodales etiam; urna nisi. Finibus montes hendrerit ligula sed dapibus maximus congue. Vivamus hac ipsum; scelerisque fringilla velit montes habitant. Erat porta scelerisque duis porta pretium natoque eget. Metus penatibus felis, inceptos dis laoreet eget. Curae suspendisse eleifend suspendisse eros nulla curae sed primis. Nulla vitae habitant tortor consequat ultrices pretium maecenas aliquet dignissim.

                                    </SheetDescription>
                                </SheetHeader>
                            </SheetContent>

                        </Sheet>

                    </motion.div>
                    }
                </AnimatePresence>
                {showLogout && <motion.div key="profile" className="o-ml-auto">

                    <DropdownMenu modal={false} >
                        <DropdownMenuTrigger asChild>

                            <div className=" o-w-[32px] o-h-[32px] @sm:o-w-[48px] @sm:o-h-[48px] o-border o-flex o-items-center o-justify-center o-rounded-full o-cursor-pointer">
                                <Icon className="o-select-none">
                                    person
                                </Icon>
                            </div>

                        </DropdownMenuTrigger>
                        <DropdownMenuContent className="!o-w-12" side="bottom" align="end">
                            <DropdownMenuItem asChild>
                                <div className="o-flex o-flex-row o-gap-1 o-w-full" onClick={() => { logout(); closeMobileMenu(); }}>
                                    <Icon>logout</Icon><p className="o-pl-2">Logout</p>
                                </div>
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                </motion.div>}
            </div>
        </nav>



    )
}

export default Toolbar