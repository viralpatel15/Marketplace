'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { api } from '@/lib/api'

interface Stats {
  total_companies: number; total_products: number; active_subscriptions: number
  new_signups_today: number; mrr: number
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<Stats | null>(null)

  useEffect(() => {
    api.get('/api/admin/stats').then(r => setStats(r.data.data)).catch(() => {})
  }, [])

  const cards = stats ? [
    { label: 'Total Companies', value: stats.total_companies },
    { label: 'Active Products', value: stats.total_products },
    { label: 'Active Subscriptions', value: stats.active_subscriptions },
    { label: 'New Today', value: stats.new_signups_today },
    { label: 'MRR', value: `₹${stats.mrr.toLocaleString()}` },
  ] : []

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Admin Dashboard</h1>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
        {cards.map((c) => (
          <div key={c.label} className="bg-white border border-gray-200 rounded-xl p-5">
            <p className="text-2xl font-bold text-gray-900">{c.value}</p>
            <p className="text-xs text-gray-500 mt-1">{c.label}</p>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { href: '/admin/companies/pending', label: 'Pending Verifications', desc: 'Review GST verification requests' },
          { href: '/admin/companies', label: 'Manage Companies', desc: 'View and manage all seller profiles' },
          { href: '/admin/products', label: 'Manage Products', desc: 'Feature products, remove violations' },
          { href: '/admin/categories', label: 'Categories', desc: 'Add and manage product categories' },
          { href: '/admin/subscriptions', label: 'Subscriptions', desc: 'View MRR and subscription status' },
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
