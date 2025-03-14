import { HelmetProvider } from "./helmet.provider";
import { ThemeProvider } from "./theme.provider"
import { TooltipProvider } from "./tooltip.provider";

const Providers = ({ children }) => {
    return (
        <HelmetProvider>
            <ThemeProvider>
                <TooltipProvider>
                    {children}
                </TooltipProvider>
            </ThemeProvider>
        </HelmetProvider>
    )
}

export default Providers;