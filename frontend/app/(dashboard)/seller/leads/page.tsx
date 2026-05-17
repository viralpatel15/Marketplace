'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

interface Lead {
  id: number; buyer_name: string; buyer_phone: string; buyer_email: string
  buyer_city: string; quantity: number; source: string; is_viewed: boolean
  created_at: string; product_id: number
}

export default function LeadsPage() {
  const [leads, setLeads] = useState<Lead[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/api/leads').then(r => {
      setLeads(r.data.data)
      setTotal(r.data.meta?.total || 0)
    }).finally(() => setLoading(false))
  }, [])

  const markViewed = async (id: number) => {
    await api.put(`/api/leads/${id}/viewed`)
    setLeads(leads.map(l => l.id === id ? { ...l, is_viewed: true } : l))
  }

  if (loading) return <div className="p-8 text-center text-gray-500">Loading leads...</div>

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Leads Inbox</h1>
        <span className="text-sm text-gray-500">{total} total leads</span>
      </div>

      {leads.length === 0 ? (
        <div className="text-center py-16 text-gray-500">No leads yet. Add products to start receiving inquiries.</div>
      ) : (
        <div className="space-y-4">
          {leads.map((lead) => (
            <div key={lead.id} className={`bg-white border rounded-xl p-5 ${!lead.is_viewed ? 'border-blue-300 shadow-sm' : 'border-gray-200'}`}>
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-gray-900">{lead.buyer_name}</h3>
                    {!lead.is_viewed && <span className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded-full">New</span>}
                  </div>
                  <p className="text-sm text-gray-600">{lead.buyer_city} · Qty: {lead.quantity || 'Not specified'}</p>
                  <div className="mt-2 flex gap-4 text-sm">
                    <span>📞 {lead.buyer_phone}</span>
                    <span>✉️ {lead.buyer_email}</span>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-400">{new Date(lead.created_at).toLocaleDateString()}</p>
                  {!lead.is_viewed && (
                    <button onClick={() => markViewed(lead.id)} className="mt-2 text-xs text-blue-600 hover:underline">Mark as viewed</button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
