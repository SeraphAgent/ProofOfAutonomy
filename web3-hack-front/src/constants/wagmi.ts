import { createConfig, http } from 'wagmi'
import { base } from 'wagmi/chains'

export function getConfig() {
  return createConfig({
    chains: [base],
    ssr: false,
    transports: {
      [base.id]: http(),
    },
  })
}

declare module 'wagmi' {
  interface Register {
    config: ReturnType<typeof getConfig>
  }
}
