import { BACKEND_URL } from "./constants"

const headers = {
    'Content-Type': 'application/json',
}

export const signUp = async (shortCode, params={}) => {
    const response = await fetch(`${BACKEND_URL}/signup`, {
        method: 'POST',
        headers,
        credentials: 'include',
        body: JSON.stringify({
            account_shortcode: shortCode,
            ...params,
        }),
    })
    return response
}

export const login = async (params={}) => {
    const response = await fetch(`${BACKEND_URL}/login`, {
        method: 'POST',
        headers,
        credentials: 'include',
        body: JSON.stringify({
            ...params,
        }),
    })
    return response
}

export const logout = async () => {
    const response = await fetch(`${BACKEND_URL}/logout`, {
        method: 'POST',
        headers,
        credentials: 'include',
    })
    return response
}

export const validate = async () => {
    const response = await fetch(`${BACKEND_URL}/validate`, {
        method: 'POST',
        headers,
        credentials: 'include'
    })
    return response
}

export const sendMessage = async (message, sessionId) => {
    const response = await fetch(`${BACKEND_URL}/chat`, {
        method: 'POST',
        headers,
        credentials: 'include',
        body: JSON.stringify({
            session_id: sessionId,
            message: {
                role: "user",
                content: message
            }
        })
    })
    if (!response.ok) {
        throw new Error('Network response was not ok')
    }
    return response
}

export const newChat = async (assistantId) => {
    const response = await fetch(`${BACKEND_URL}/chat/session`, {
        method: 'POST',
        headers,
        credentials: 'include',
        body: JSON.stringify({
            assistant_id: assistantId
        }),
    })
    const json = await response.json();
    if (!response.ok) {
        throw new Error(json?.detail ?? 'Network response was not ok')
    }
    return json
}

export const getChat = async (sessionId) => {
    const response = await fetch(`${BACKEND_URL}/chat/messages?session_id=${sessionId}`, {
        method: 'GET',
        credentials: 'include',
        headers
    })
    const json = await response.json();
    // console.log("getChat messages", json)
    if (!response.ok) {
        throw new Error(json?.detail ?? 'Network response was not ok')
    }
    return json
}

export const getChats = async () => {
    const response = await fetch(`${BACKEND_URL}/chat/session`, {
        method: 'GET',
        credentials: 'include',
        headers
    })
    const json = await response.json();
    if (!response.ok) {
        throw new Error(json?.detail ?? 'Network response was not ok')
    }
    return json
}

export const getAssistants = async () => {
    const response = await fetch(`${BACKEND_URL}/assistant`, {
        method: 'GET',
        credentials: 'include',
        headers
    })
    const json = await response.json();
    if (!response.ok) {
        throw new Error(json?.detail ?? 'Network response was not ok')
    }
    return json
}

export const sendFeedback = async (messageId, weight) => {
    const response = await fetch(`${BACKEND_URL}/chat/feedback`, {
        method: 'POST',
        credentials: 'include',
        headers,
        body: JSON.stringify({

            message_id: messageId,
            feedback: weight
        }),
    })
    const json = await response.json();
    if (!response.ok) {
        throw new Error(json?.detail ?? 'Network response was not ok')
    }
    return json
}

export const getAccount = async (shortCode) => {
    const response = await fetch(`${BACKEND_URL}/account?short_code=${shortCode}`, {
        method: 'GET',
        credentials: 'include',
        headers
    })
    const json = await response.json();
    if (!response.ok) {
        throw new Error(json?.detail ?? 'Network response was not ok')
    }
    return json
}

export const getAppConfig = async (shortCode) => {
    const response = await fetch(`${BACKEND_URL}/account/config/${shortCode}`, {
        method: 'GET',
        credentials: 'include',
        headers
    })
    const json = await response.json();
    if (!response.ok) {
        throw new Error(json?.detail ?? 'Network response was not ok')
    }
    return json
}

// General app fetch 
export const grab = async (url, method="GET", body=null) => {
    console.log(method, body, url)
    const response = await fetch(url, {
        method: method,
        credentials: 'include',
        headers,
        body: body ? JSON.stringify(body) : null
    })
    const json = await response.json();
    if (!response.ok) {
        throw new Error(json?.detail ?? 'Network response was not ok')
    }
    return json
}
