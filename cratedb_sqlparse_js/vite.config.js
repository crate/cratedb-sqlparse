// vite.config.js
import {
    resolve
} from 'path'
import {
    defineConfig
} from 'vite'

export default defineConfig({
    build: {
        lib: {
            // Could also be a dictionary or array of multiple entry points
            entry: resolve(__dirname, 'parser/index.js'),
            name: 'cratedb_sqlparse', // the proper extensions will be added
            fileName: 'sqlparse',
        }, rollupOptions: {
            // make sure to externalize deps that shouldn't be bundled
            // into your library
            external: [], output: {},
        },
    },
})