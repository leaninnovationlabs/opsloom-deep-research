# LIL RAG

Built in Vite with HMR and some ESLint rules.

- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh


## Getting Started 

`cd ui`

`npm run dev`

## Adding new components

`npx shadcn-ui@latest add <COMPONENTS>`

or you can copy/paste

see [Shadcn Documentation](https://ui.shadcn.com/docs)

# Building the Embedable Widget

`npm build`

Then copy over the generated `index-ABC123.css` and `index-CBA321.js` that is generated and throw it in your projects `/public` folder .. then add then in `index.html` add these tags to `<head/>` :

`<link rel="stylesheet" crossorigin href="/index-ABC123.css">`
`<script type="module" crossorigin src="/index-CBA321.js"></script>`

And this one to `<body/>`:

`<div id="opsloom-chat" data-api-url="http://localhost:8080" data-not-widget></div>`


# Notes on Styling
## Warning - This whole app uses container queries (rather media queries)

Because we have wrapped this whole app with a CSS `@container` for embedding purposes, we need to use `@` before all size selectors or else the embedded app will take the dimementions of the hosted app window rather it's inherant pre-set size. You also will have to be careful where you use `fixed` for this same reason and instead lean more toward `absolute`. Also be careful about using `screen`, `vh`, `vw`, `dvh`, `dvw` etc

## Prefix every Tailwind Style with -o

To avoid conflicts with other tailwind apps, this app only accepts tailwind classes with the `-o` prefix. So for example, instead of using `h-full` you need to use `o-h-full`