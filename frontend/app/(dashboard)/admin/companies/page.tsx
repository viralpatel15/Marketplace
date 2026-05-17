'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

interface Company {
  id: number; name: string; city: string; category: string; is_verified: boolean; total_leads: number
}

export default function AdminCompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([])
  const [total, setTotal] = useState(0)

  useEffect(() => {
    api.get('/api/admin/companies').then(r => {
      setCompanies(r.data.data)
      setTotal(r.data.meta?.total || 0)
    })
  }, [])

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">All Companies ({total})</h1>
      <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-600 font-medium">
            <tr>
              <th className="text-left px-4 py-3">Company</th>
              <th className="text-left px-4 py-3">City</th>
              <th className="text-left px-4 py-3">Category</th>
              <th className="text-left px-4 py-3">Verified</th>
              <th className="text-left px-4 py-3">Leads</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {companies.map((c) => (
              <tr key={c.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-900">{c.name}</td>
                <td className="px-4 py-3 text-gray-600">{c.city}</td>
                <td className="px-4 py-3 text-gray-600">{c.category}</td>
                <td className="px-4 py-3">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${c.is_verified ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                    {c.is_verified ? 'Verified' : 'Pending'}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-600">{c.total_leads}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
