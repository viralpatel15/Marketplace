'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { api } from '@/lib/api'

interface Stats {
  total_views: number; total_leads: number; total_inquiries: number; conversion_rate: number
}

export default function SellerDashboard() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [sub, setSub] = useState<{ plan: string; products_used: number; max_products: number } | null>(null)

  useEffect(() => {
    api.get('/api/analytics/overview').then(r => setStats(r.data.data)).catch(() => {})
    api.get('/api/subscribe/status').then(r => setSub(r.data.data)).catch(() => {})
  }, [])

  const cards = [
    { label: 'Product Views (30d)', value: stats?.total_views ?? '—' },
    { label: 'Leads (30d)', value: stats?.total_leads ?? '—' },
    { label: 'Inquiries (30d)', value: stats?.total_inquiries ?? '—' },
    { label: 'Conversion Rate', value: stats ? `${stats.conversion_rate}%` : '—' },
  ]

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Seller Dashboard</h1>
        <div className="flex gap-3">
          <Link href="/seller/products/new" className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700">+ Add Product</Link>
        </div>
      </div>

      {sub && sub.plan === 'Free' && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6 flex items-center justify-between">
          <p className="text-amber-800 text-sm">You&apos;re on the Free plan. Upgrade to see full contact details of leads.</p>
          <Link href="/seller/subscription" className="bg-amber-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-amber-600">Upgrade Plan</Link>
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {cards.map((c) => (
          <div key={c.label} className="bg-white border border-gray-200 rounded-xl p-5">
            <p className="text-3xl font-bold text-gray-900">{c.value}</p>
            <p className="text-sm text-gray-500 mt-1">{c.label}</p>
          </div>
        ))}
      </div>

      {sub && (
        <div className="bg-white border border-gray-200 rounded-xl p-5 mb-6">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-gray-900">Plan: {sub.plan}</h3>
            <Link href="/seller/subscription" className="text-blue-600 text-sm hover:underline">Manage</Link>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-2">
            <div className="bg-blue-600 h-2 rounded-full" style={{ width: sub.max_products === -1 ? '20%' : `${Math.min((sub.products_used / sub.max_products) * 100, 100)}%` }} />
          </div>
          <p className="text-xs text-gray-500 mt-1">{sub.products_used} of {sub.max_products === -1 ? 'unlimited' : sub.max_products} products used</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { href: '/seller/products', label: 'Manage Products', desc: 'Add, edit or delete your listings' },
          { href: '/seller/leads', label: 'View Leads', desc: 'See buyer inquiries and contact details' },
          { href: '/seller/profile', label: 'Edit Profile', desc: 'Update your company information' },
        ].map((item) => (
          <Link key={item.href} href={item.href} className="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md transition-shadow">
            <h3 className="font-semibold text-gray-900 mb-1">{item.label}</h3>
            <p className="text-sm text-gray-500">{item.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
