import { Helmet } from "react-helmet"

const HelmetProvider = ({ children, ...props }) => {
    return (
        <>
            <Helmet>
                <link rel="stylesheet"
                    href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20,200,0,0" />
            </Helmet>
            {children}
        </>
    )
}

export { HelmetProvider };