// vite.config.js
import {
    resolve
} from 'path'
import {
    defineConfig
} from 'vite'
import packageJson from './package.json';

export default defineConfig({
    build: {
        minify: "terser",
        lib: {
            // Could also be a dictionary or array of multiple entry points
            entry: resolve(__dirname, 'cratedb_sqlparse/index.js'),
            name: packageJson.name, // the proper extensions will be added
            fileName: 'sqlparse',
        }, rollupOptions: {
            // make sure to externalize deps that shouldn't be bundled
            // into your library
            external: [],
            output: {},
        },
    },
})