import React from 'react'

export default function Stars({ rarity }: { rarity?: string }) {
  const m = String(rarity || '').match(/(\d+)/)
  const n = m ? Math.max(1, Math.min(6, Number(m[1]))) : 0
  return (
    <span className="stars" title={rarity}>
      {Array.from({ length: n }).map((_, i) => (
        <span key={i}>★</span>
      ))}
    </span>
  )
}
