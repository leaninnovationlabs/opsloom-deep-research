import Icon from "@/components/Icon";
import { Button } from "@/components/ui/button";
import { LIL_MAIN_SITE } from "@/lib/constants";
import useAppConfigStore from "@/lib/store/appconfig.store";
import useChatStore from "@/lib/store/chat.store";
import { cn, transition } from "@/lib/utils";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { useMemo } from "react";
import { Link } from "react-router-dom";


const Home = (props) => {
    const assistants = useChatStore(state => state.assistants);
    const { welcomeText, h1, h2 } = useAppConfigStore(state => state.i18n.home)
    const shouldReduceMotion = useReducedMotion();

    const items = useMemo(() => {
        return assistants.length < 4 ? assistants.slice(0, 4).concat(Array(Math.max(0, 4 - assistants.length)).fill(null)) : assistants
    }, [assistants])


    const ready = useMemo(() => assistants.length > 0, [assistants]);

    return (



        <div className="o-min-w-3xl o-w-fit o-mx-auto @lg:o-pt-[clamp(50px,calc(100vh-1000px),200px)] o-p-6">
            <AnimatePresence>
                {ready &&
                    <motion.div key="intro" className="o-mb-16" {...transition(0, shouldReduceMotion)} >
                        <h1 className="o-text-6xl o-leading-[1.1] o-font-medium o-bg-[linear-gradient(90deg,rgb(255,0,230,80%)_3.08%,rgb(255,0,100)_100%)] o-w-fit o-bg-clip-text o-text-transparent o-fill-transparent">
                            {h1}
                        </h1>
                        <h2 className="o-text-5xl o-leading-[1.1] o-font-medium o-text-foreground/20">
                            {h2}
                        </h2>
                    </motion.div>}

                {ready &&
                    <motion.div key="cards" className="o-grid o-grid-cols-1 @md:o-grid-cols-2 @xl:o-grid-cols-4 o-gap-6 o-mb-12" {...transition(1, shouldReduceMotion)} >


                        {
                            items.map((ass, idx) => (
                                <Link to={`/assistant/${ass?.id}`} key={idx}
                                    className={cn("o-relative o-bg-card o-text-card-foreground o-w-full @2xl:o-w-[300px] o-h-[210px] o-border o-rounded-lg o-p-4 o-flex o-flex-col o-gap-2 o-leading-snug o-select-none o-group o-transition-colors", ass ? "hover:o-bg-muted" : "o-cursor-not-allowed o-pointer-events-none o-bg-muted dark:o-bg-transparent")}>
                                    <Icon className="o-border o-rounded-lg o-w-fit o-h-fit o-p-1 o-bg-muted">
                                        {ass?.metadata?.icon ? ass.metadata.icon : "hourglass"}
                                    </Icon>
                                    <h3 className={cn(!ass && "o-text-muted-foreground")}>
                                        {ass?.metadata?.title ? ass.metadata.title : "Something Really Cool"}
                                    </h3>
                                    <p className="o-text-card-foreground/30 o-overflow-y-hidden o-line-clamp-3 ">
                                        {ass?.metadata?.description ? ass.metadata.description : "Coming soon"}
                                    </p>
                                </Link>

                            ))
                        }
                    </motion.div>}
                {ready &&
                    <motion.div key="detail" className={cn(welcomeText?.length && welcomeText.length > 200 ? "o-w-full" : "@xl:o-w-[calc(50%-12px)]", "o-relative o-flex @sm:o-mb-[70px] o-rounded-lg o-p-6 @xl:o-p-8 @xl:o-pt-5 @xl:o-pb-6 o-max-w-[1272px] dark:o-bg-[radial-gradient(circle,rgba(57,9,133,0.5)_0%,rgba(194,38,70,0.5)_100%)] o-bg-[radial-gradient(circle,rgba(155,101,240,0.1)_0%,_rgba(194,38,179,0.1)_100%)] o-border")} {...transition(2, shouldReduceMotion)} >
                        <div className="o-inline-block o-w-fit">
                            <Icon className="o-rounded-lg o-w-fit o-h-fit o-p-1 o-bg-muted o-border dark:o-border-none dark:o-bg-foreground/20 mb-3">
                                rocket
                            </Icon>
                            <h1 className="o-text-xl o-mb-3">
                                Jump Start your AI Effort
                            </h1>
                            <p className="o-text-muted-foreground o-leading-tight">
                                {welcomeText ?? ""}
                            </p>
                            <Button variant="link" className="o-hidden @md:o-inline -o-ml-4 o-mt-3" onClick={() => window.open(LIL_MAIN_SITE, "_blank")}>
                                {`Learn More >`}
                            </Button>
                            <Button variant="default" className="@md:o-hidden o-flex o-w-full o-mt-6 @xl:o-max-w-[200px]">
                                {`Learn More >`}
                            </Button>
                        </div>
                        {/* <img src="/squiggly.png" alt="squiggly neon lines bg" className="top-0 left-0 absolute w-full h-full opacity-20 bg-cover object-cover fill rounded-lg" fetchpriority="high" /> */}
                    </motion.div>}
            </AnimatePresence>



        </div>
    )
}

export default Home;