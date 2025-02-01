import { defineConfig } from 'tsup'

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm'],
  dts: true,
  clean: true,
  splitting: false,
  sourcemap: true,
  external: [
    '@elizaos/core',
    '@elizaos/client-twitter',
    'openai',
  ],
  esbuildOptions(options) {
    options.platform = 'node'
    options.target = 'node18'
  }
})