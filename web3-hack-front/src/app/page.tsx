'use client'

import { DigitalRain } from '@/components/DigitalRain'
import Portfolio from '@/components/Portfolio'
import { useEffect, useState } from 'react'

export default function Home() {
  const [transactions, setTransactions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [fetching, setFetching] = useState(false)

  const fetchTransactions = async () => {
    setFetching(true)
    try {
      const response = await fetch(
        'https://base-mainnet.g.alchemy.com/v2/wsd_hYGsJKSi3286xQU2XDKmhzn1airy',
        {
          method: 'POST',
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            id: 1,
            jsonrpc: '2.0',
            method: 'alchemy_getAssetTransfers',
            params: [
              {
                fromBlock: '0x0',
                toBlock: 'latest',
                category: ['erc20'],
                order: 'desc',
                withMetadata: false,
                excludeZeroValue: true,
                maxCount: '0x1E',
                contractAddresses: [
                  '0x4f81837C2f4A189A0B69370027cc2627d93785B4',
                ],
                fromAddress: '0xe2f3b3129b33a535f1bf9c8edac50d3bdee420cc',
              },
            ],
          }),
        }
      )

      const data = await response.json()
      if (data.result && data.result.transfers) {
        setTransactions((prev) => {
          const newTransactions = data.result.transfers
          const existingHashes = new Set(prev.map((tx) => tx.hash))
          const filteredNew = newTransactions.filter(
            (tx: any) => !existingHashes.has(tx.hash)
          )
          return [...filteredNew, ...prev]
        })
      }
    } catch (error) {
      console.error('Error fetching transactions:', error)
    } finally {
      setLoading(false)
      setFetching(false)
    }
  }

  useEffect(() => {
    fetchTransactions()
    const interval = setInterval(fetchTransactions, 60000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="relative flex min-h-screen items-center justify-center bg-black overflow-hidden">
      <DigitalRain />

      {/* Main Content Wrapper */}
      <div className="relative z-10 w-full max-w-4xl p-8 rounded-lg border border-green-500/50 bg-gray-900 shadow-xl text-white">
        {/* Main Title */}
        {!loading ? (
          <>
            <h1 className="text-3xl font-bold mb-6 text-green-400 text-center">
              Verifiable Inference
            </h1>

            <Portfolio />

            {/* Added Spacing Between Portfolio and Bounty Board */}
            <div className="mt-8"></div>

            {/* Section Title */}
            <h2 className="text-2xl font-semibold mb-6 text-center text-green-300">
              Bounty Board
            </h2>
          </>
        ) : null}

        {/* Show "Loading transactions..." only on first load */}
        {loading ? (
          <div className="text-center text-green-400 font-mono animate-pulse">
            Loading transactions...
          </div>
        ) : (
          <>
            {/* Show "Fetching new transactions..." when updating */}
            {fetching && (
              <div className="text-center text-green-400 font-mono animate-pulse mb-4">
                Fetching new transactions...
              </div>
            )}

            <div className="space-y-3 overflow-y-auto max-h-[70vh] font-mono text-base px-4">
              {transactions.map((tx, i) => (
                <div
                  key={tx.hash || i}
                  className="p-6 bg-gray-800 rounded-xl shadow-md flex flex-col items-center w-full"
                >
                  <p className="text-green-400 font-bold text-lg">
                    +{tx.value} {tx.asset}
                  </p>
                  <p className="text-gray-400 text-sm">{tx.to}</p>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
