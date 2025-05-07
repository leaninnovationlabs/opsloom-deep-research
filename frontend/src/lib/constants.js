const root = document.getElementById("opsloom-chat");
export const LIL_MAIN_SITE = "https://www.leaninnovationlabs.com/";

export const MODE_TYPES = {
    BUBBLE_WIDGET: "bubble-widget", // Little helper in the corner
    FILL_PARENT: "fill-parent", // fills parent container
    WEBAPP: "webapp" // complete webapp that takes over the router
}

export const MODE = root?.dataset?.moduleType || MODE_TYPES.FILL_PARENT;

if(MODE === MODE_TYPES.FILL_PARENT) {
    root.style.height = "inherit";
    root.style.width = "inherit";
}

export const FORCED_THEME = ['light', 'dark'].includes(root?.dataset?.forcedTheme) ? root?.dataset?.forcedTheme : false;

export const HEADLESS = ["true", ""].includes(root?.dataset?.headless ?? false) ? true : false


export const BACKEND_URL = (
    // Check for environment variable first  
    `http://localhost:8080/opsloom-api/v1`
  )

console.log("BACKEND_URL:", BACKEND_URL);

export const ROUTER_BASE_URL = MODE === MODE_TYPES.WEBAPP ? "opsloom" : "";