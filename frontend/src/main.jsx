import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import Providers from './lib/providers/index.jsx'


ReactDOM.createRoot(document.getElementById("opsloom-chat")).render(
  <Providers>
    <App/>
  </Providers>
)
