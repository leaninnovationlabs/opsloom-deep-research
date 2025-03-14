import { create } from 'zustand'
import { sendMessage, newChat, getChat, getChats, getAssistants } from '@/lib/api'
import { immer } from 'zustand/middleware/immer'


const INIT = {
    ready: false,
    messages: [],
    sessionId: null,
    isLoading: false,
    isThinking: false,
    history: [],
    assistants: [],
    assistant: {},
    messageInQueue: false,
    input: "",
    abort: false, 
}

const useChatStore = create(immer((set, get) => ({
    ...INIT,

    // Needs to stay hydrated by Chat and Assistant Components
    setAssistant: (id) => {set(state => {return({ ...state, assistant: get().assistants.find(x => x.id === id) })})},

    queueMessage: () => set(state => ({ ...state, messageInQueue: true })),

    setInput: (input) => set(state => ({ ...state, input })),

    initStore: async () => {
        // WARNING: You must be logged in before activating the store


        // load in assistants
        try {
            await get()._loadAssistants();

            // load in history
            await get().refreshHistory();

            set((state) => { state.ready = true })
        }
        catch (error) {
            console.error("There was a problem activating the chat store. Are you logged in?", error)
        }

    },
    resetStore: () => {
        set(state => ({
            ...state,
            ...INIT,
            ready: true
        }))
    },
    _loadAssistants: async () => {
        const response = await getAssistants();
        set((state) => ({
            ...state,
            assistants: response.assistants,
        }))
    },
    refreshHistory: async () => {
        const response = await getChats();
        set((state) => ({
            ...state,
            history: response.list
        }))
    },
    clearChat: () => {
        set((state) => ({
            ...state,
            sessionId: null,
            isLoading: false,
            isThinking: false,
            abort: false,
            messageInQueue: false, //TODO: problems?
            messages: [],
        }))
    },

    loadChat: async (sessionId) => {

        set((state) => ({
            ...state,
            abort: true,
            isThinking: false,
            isLoading: true,
            messages: []
        }))

        const response = await getChat(sessionId)

        // update target assistant (granted one assistant per chat)
        const assistantId = get().history.find(y => y.id === sessionId)?.assistant_id
        const assistant = get().assistants.find(x => x.id === assistantId)
        
        set((state) => {
            return ({
                ...state,
                messages: response.messages,
                sessionId,
                assistant,
                isLoading: false
            })
        })


    },
    sendMessage: async () => {

        set(state => ({ ...state, messageInQueue: false }))

        const message = get().input;
        if (!message.trim()) return

        set(state => ({ ...state, input: "" }))

        const oldMessages = [
            ...get().messages,
            { blocks: message, role: 'user' },
        ]

        set((state) => ({
            ...state,
            messages: [
                ...oldMessages,
                { blocks: [], role: 'ai' },
            ],
            isLoading: true,
            isThinking: true,
            abort: false,
        }))


        let sessionId = get().sessionId
        // create new session

        if (!sessionId) {
            const response = await newChat(get().assistant?.id)

            sessionId = response.session.id;


            set(state => ({ ...state, sessionId }))
        }

        try {

            const response = await sendMessage(message, sessionId)
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { value, done } = await reader.read();
                if (done || get().abort === true) {
                    set(state => ({ ...state, abort: false, isLoading: false, isThinking: false }))
                    break;
                }

                const decodedChunk = decoder.decode(value);
                const lines = decodedChunk.split('\n');

                let updatedTitle = false;
                for (const line of lines) {
                    if (line.trim()) {
                        const data = JSON.parse(line);

                        set((state) => ({
                            ...state,
                            messages: [
                                ...oldMessages,
                                {
                                    blocks: data.blocks, message_id: data.message_id, role: 'ai', sources: response.sources,
                                    // assistant_id: data.assistant_id
                                }
                            ],
                            isThinking: false
                        }))


                        // Update title if it's ready
                        if (data?.title && !updatedTitle) {
                            set(state => {
                                let found = state.history.findIndex(x => x.id === sessionId)
                                if (found !== -1) {
                                    state.history[found].title = data.title;
                                }
                                else {
                                    console.warn("strange issue: cannot find sessionId")
                                }
                            })
                            updatedTitle = true
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error:', error)
            set((state) => ({
                ...state,
                messages: [...state.messages, { text: 'An error occurred. Please try again.', role: 'ai' }],
                isLoading: false
            }))
        }
    },
    refreshHomeScreen: () => {
        const assistants = [...get().assistants]
        set(state => { state.assistants = [] });
        setTimeout(() => set(state => { state.assistants = assistants }), 300);
    }
})))

export default useChatStore