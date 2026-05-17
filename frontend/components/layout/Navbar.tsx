'use client'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

export default function Navbar() {
  const router = useRouter()
  const [q, setQ] = useState('')

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (q.trim()) router.push(`/products?q=${encodeURIComponent(q.trim())}`)
  }

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 flex items-center gap-4 h-16">
        <Link href="/" className="text-2xl font-bold text-blue-600 shrink-0">YourMarket</Link>
        <form onSubmit={handleSearch} className="flex-1 max-w-xl">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search products, suppliers..."
            className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500"
          />
        </form>
        <div className="flex items-center gap-3 ml-auto">
          <Link href="/products" className="text-sm text-gray-600 hover:text-blue-600">Products</Link>
          <Link href="/login" className="text-sm text-gray-600 hover:text-blue-600">Login</Link>
          <Link href="/register" className="bg-blue-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-blue-700">
            List Your Products
          </Link>
        </div>
      </div>
    </nav>
  )
}
