import { clsx } from "clsx"
import { extendTailwindMerge } from "tailwind-merge";

export const twMerge = extendTailwindMerge({
  prefix: "o-",
});

export function cn(...inputs) {
    return twMerge(clsx(inputs))
}

export const getLocalStorage = (key) => window.localStorage.getItem(key);

export const setLocalStorage = (key, value) => window.localStorage.setItem(key, value);

export function getSessionIdFromLocation(location) {
    return location.pathname.split("/").at(-1)
}

export function isNewChatLocation(location) {
    return location.pathname.split("/").includes("assistant")
}

export function getGreeting() {
    var today = new Date()
    var curHr = today.getHours()

    if (curHr < 12) {
        return "Good morning,";
    } else if (curHr < 18) {
        return "Good afternoon,";
    } else {
        return "Good evening,";
    }
}

export const transition = (delay = 0, reduceMotion = false) => {
    if (!reduceMotion) {
        return (
            { initial: { y: -30, opacity: 0 }, animate: { y: 0, opacity: 1 }, exit: { opacity: 0, transition: { duration: .2 } }, transition: { type: "spring", stiffness: 300, damping: 50, delay: delay * 0.07 } }
        )
    }
    return {
        initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0, transition: { duration: .2 } }, transition: { type: "spring", stiffness: 300, damping: 50 }
    }
}

export const getShortCode = () => {
    const hostname = window.location.hostname;
    const urlParams = new URLSearchParams(window.location.search);
    const accountParam = urlParams.get('account');

    if (hostname === 'chat.opsloom.io') {
        return accountParam || 'default';
    }
    
    if (hostname === 'localhost') {
      return accountParam || 'default';
    }

    if (hostname.startsWith('172.')) {
        return accountParam || 'default';
    }
    
    const subdomain = hostname.split('.')[0];
    
    if (subdomain && subdomain !== 'www') {
      return subdomain;
    }
    
    // Fall back to URL param or default
    return accountParam || 'default';
  }

export function validateEmail(email) {
    const REGEX =
      "^((([a-z]|\\d|[!#\\$%&'\\*\\+\\-\\/=\\?\\^_`{\\|}~]|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF])+(\\.([a-z]|\\d|[!#\\$%&'\\*\\+\\-\\/=\\?\\^_`{\\|}~]|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF])+)*)|((\\x22)((((\\x20|\\x09)*(\\x0d\\x0a))?(\\x20|\\x09)+)?(([\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x7f]|\\x21|[\\x23-\\x5b]|[\\x5d-\\x7e]|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF])|(\\\\([\\x01-\\x09\\x0b\\x0c\\x0d-\\x7f]|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF]))))*(((\\x20|\\x09)*(\\x0d\\x0a))?(\\x20|\\x09)+)?(\\x22)))@((([a-z]|\\d|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF])|(([a-z]|\\d|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF])([a-z]|\\d|-|\\.|_|~|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF])*([a-z]|\\d|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF])))\\.)+(([a-z]|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF])|(([a-z]|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF])([a-z]|\\d|-|\\.|_|~|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF])*([a-z]|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF])))\\.?$";
  
    const regex = new RegExp(REGEX);
    const matches = regex.test(email.toLowerCase());
    return matches
  }
