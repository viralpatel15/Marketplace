'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

interface Company {
  id: number; name: string; city: string; category: string; gst_number: string; logo_url: string | null; is_verified: boolean
}

export default function PendingVerificationsPage() {
  const [companies, setCompanies] = useState<Company[]>([])

  useEffect(() => {
    api.get('/api/admin/companies/pending').then(r => setCompanies(r.data.data))
  }, [])

  const verify = async (id: number) => {
    await api.put(`/api/admin/companies/${id}/verify`)
    setCompanies(companies.filter(c => c.id !== id))
  }

  const reject = async (id: number) => {
    const reason = prompt('Rejection reason:')
    if (!reason) return
    await api.put(`/api/admin/companies/${id}/reject`, { reason })
    setCompanies(companies.filter(c => c.id !== id))
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Pending GST Verifications ({companies.length})</h1>
      {companies.length === 0 ? (
        <div className="text-center py-16 text-gray-500">No pending verifications.</div>
      ) : (
        <div className="space-y-4">
          {companies.map((c) => (
            <div key={c.id} className="bg-white border border-gray-200 rounded-xl p-5">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900">{c.name}</h3>
                  <p className="text-sm text-gray-500">{c.category} · {c.city}</p>
                  <p className="text-sm font-mono bg-gray-100 px-2 py-0.5 rounded mt-1 inline-block">GST: {c.gst_number}</p>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => verify(c.id)} className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-700">Verify</button>
                  <button onClick={() => reject(c.id)} className="bg-red-50 text-red-600 border border-red-200 px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-100">Reject</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
