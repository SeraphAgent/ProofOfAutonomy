'use client'

import { ethosContractConfig } from '@/constants/contract-config'
import Image from 'next/image'
import { useReadContract } from 'wagmi'

export default function Portfolio() {
  const profileId = 898 // AIXBT profile ID

  // Fetch trust and distrust votes
  const { data: rawVotes, isLoading } = useReadContract({
    ...ethosContractConfig,
    functionName: 'getUserVotes',
    args: ['0x07D5A0A089c7E5cbd5095B5bc3A242A21C0a8D60', profileId],
    query: {
      refetchInterval: 30000,
    },
  })

  // Parse response safely
  const trustAmount = rawVotes ? Number((rawVotes as any).trustVotes) : 0
  const distrustAmount = rawVotes ? Number((rawVotes as any).distrustVotes) : 0

  return (
    <div className="flex flex-col items-center justify-center w-full max-w-lg p-6 rounded-lg border border-green-500 bg-gray-900 shadow-xl text-white mt-8">
      {/* Portfolio Title */}
      <h2 className="text-2xl font-bold mb-4 text-green-400 text-center">
        Portfolio
      </h2>

      {/* Image Container with Navigation Buttons */}
      <div className="relative flex items-center justify-center w-full">
        {/* Disabled Left Button */}
        <button className="absolute left-0 p-2 bg-gray-800 border border-gray-600 text-gray-500 rounded-md cursor-not-allowed opacity-50">
          ◀
        </button>

        {/* Image in the Center */}
        <div className="relative w-40 h-40 mx-12 border-2 border-green-500 rounded-lg shadow-lg">
          <Image
            src="/aixbt.jpg"
            alt="Portfolio"
            layout="fill"
            objectFit="cover"
            className="rounded-lg"
          />
        </div>

        {/* Disabled Right Button */}
        <button className="absolute right-0 p-2 bg-gray-800 border border-gray-600 text-gray-500 rounded-md cursor-not-allowed opacity-50">
          ▶
        </button>
      </div>

      {/* Profile Name Below Image */}
      <p className="mt-2 text-lg font-bold text-green-400 text-center">AIXBT</p>

      {/* Trust and Distrust Section with Skeleton Loader */}
      <div className="flex justify-between w-full mt-4 px-8">
        <p className="text-green-400 text-xl font-bold flex items-center">
          Trust:
          {isLoading ? (
            <span className="ml-2 w-8 h-6 bg-gray-700 rounded-md animate-pulse"></span>
          ) : (
            <span className="ml-2 text-green-400">+{trustAmount}</span>
          )}
        </p>
        <p className="text-red-500 text-xl font-bold flex items-center">
          Distrust:
          {isLoading ? (
            <span className="ml-2 w-8 h-6 bg-gray-700 rounded-md animate-pulse"></span>
          ) : (
            <span className="ml-2 text-red-500">-{distrustAmount}</span>
          )}
        </p>
      </div>
    </div>
  )
}
