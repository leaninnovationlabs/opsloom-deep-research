import { lazy, Suspense, useEffect, useMemo, useRef } from 'react';
import { Route, BrowserRouter, Routes, MemoryRouter } from "react-router-dom";
import useChatStore from '@/lib/store/chat.store.js';
import useAppConfigStore from './lib/store/appconfig.store';
import useUserStore from './lib/store/user.store';
import { useTheme } from './lib/providers/theme.provider';
import { useShallow } from 'zustand/react/shallow';
import { AnimatePresence, motion } from 'framer-motion';
import { transition } from './lib/utils';
import { MODE, MODE_TYPES, ROUTER_BASE_URL } from './lib/constants';
import { getShortCode } from './lib/utils';
import Container from './components/Container';


// WARNING: Cannot code split with Widget Bundler
// const Chat = lazy(() => import('./pages/Chat'));
// const Home = lazy(() => import('./pages/Home'));
// const Assistant = lazy(() => import('./pages/Assistant'));

import { Assistant, Chat, Error, Home, Layout, Loading } from '@/pages';



function App() {

    const [loggedIn, validate, signUp] = useUserStore(useShallow(state => [state.loggedIn, state.validate, state.signUp]));
    const [initChatStore, isChatReady] = useChatStore(useShallow(state => [state.initStore, state.ready]))
    const [initAppStore, isAppConfigReady, requiresEmail, fatalError, loadTheme] = useAppConfigStore(useShallow(state => [state.initStore, state.ready, state.requiresEmail, state.fatal, state.loadTheme]))

    const { rawTheme } = useTheme();

    // Store search params and clear from url
    // const shortCode = window.location.hostname.split('.')[0] === 'localhost' 
    // ? ((new URLSearchParams(window.location.search)).get('account') || 'default')
    // : (window.location.hostname.split('.')[0] || 'default');
    const shortCode = getShortCode();

    window.history.replaceState(null, '', window.location.pathname);

    // Reroute to /opsloom
    if (!window.location.pathname.includes(ROUTER_BASE_URL) && MODE === MODE_TYPES.WEBAPP) {
        window.history.replaceState(
            '',
            '',
            ROUTER_BASE_URL + window.location.pathname
        );
    }

    useEffect(() => {
        initAppStore(shortCode)
    }, [])

    // On light/dark theme change, reload palette
    useEffect(() => {
        if (isAppConfigReady) {
            loadTheme(rawTheme)
        }
    }, [rawTheme, isAppConfigReady])


    useEffect(() => {
        if (isAppConfigReady && !loggedIn) {
            validate();
        }
    }, [isAppConfigReady])

    useEffect(() => {
        if (loggedIn === true && !isChatReady) {
            initChatStore();
        }
        // We don't need the modal, just send this new user through
        else if (loggedIn === false && requiresEmail === false) {
            signUp(shortCode)
        }
    }, [loggedIn, requiresEmail])



    const isBooting = useMemo(() => !(isAppConfigReady && (loggedIn ? isChatReady : true)), [isAppConfigReady, isChatReady, loggedIn])

    // Do not update the url bar if the app is a widget
    const Router = (props) => MODE === MODE_TYPES.WEBAPP ? <BrowserRouter basename={ROUTER_BASE_URL} {...props} /> : <MemoryRouter {...props} />


    return (
        <Container>
            {fatalError ? <Error msg={fatalError} />
                :
                <AnimatePresence mode="wait">

                    {isBooting ?

                        <Loading className="o-h-full o-w-full o-bg-[#fff] dark:o-bg-[#09090b]" {...transition(0, true)} />

                        :
                        <motion.div key="main-content" {...transition(0, true)} className="o-h-[inherit] o-w-[inherit]">
                            <Router>
                                <Layout>
                                    <Suspense fallback={<div />}>
                                        <Routes>
                                            <Route path="/" element={<Home />} />
                                            <Route path="/assistant/*" element={<Assistant />} />
                                            <Route path="/chat/*" element={<Chat />} />
                                        </Routes>
                                    </Suspense>
                                </Layout>
                            </Router>
                        </motion.div>
                    }

                </AnimatePresence>
            }
        </Container>
    )
}

export default App
