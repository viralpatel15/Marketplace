'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

interface Company {
  name: string; city: string; state: string; category: string; phone: string
  description: string; address: string; gst_number: string; website: string; year_established: string
}

export default function SellerProfilePage() {
  const [form, setForm] = useState<Partial<Company>>({})
  const [saved, setSaved] = useState(false)
  const [loading, setLoading] = useState(false)
  const [hasCompany, setHasCompany] = useState(true)

  useEffect(() => {
    api.get('/api/companies/me').then(r => setForm(r.data.data)).catch(() => setHasCompany(false))
  }, [])

  const save = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      if (hasCompany) {
        await api.put('/api/companies/me', form)
      } else {
        await api.post('/api/companies', form)
        setHasCompany(true)
      }
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } finally {
      setLoading(false)
    }
  }

  const fields: [keyof Company, string, string?][] = [
    ['name', 'Company Name'], ['city', 'City'], ['state', 'State'], ['category', 'Business Category'],
    ['phone', 'Business Phone'], ['website', 'Website'], ['gst_number', 'GST Number'],
    ['year_established', 'Year Established', 'number'], ['address', 'Address'], ['description', 'Company Description'],
  ]

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">{hasCompany ? 'Edit Company Profile' : 'Create Company Profile'}</h1>
      <form onSubmit={save} className="bg-white border border-gray-200 rounded-xl p-6 space-y-4">
        {fields.map(([key, label, type]) => (
          <div key={key}>
            <label className="text-sm font-medium text-gray-700 block mb-1">{label}</label>
            {key === 'description' || key === 'address' ? (
              <textarea value={form[key] || ''} onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))} rows={3} className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-500" />
            ) : (
              <input type={type || 'text'} value={form[key] || ''} onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))} className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-500" />
            )}
          </div>
        ))}
        {saved && <p className="text-green-600 text-sm">Profile saved successfully!</p>}
        <button type="submit" disabled={loading} className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-60">
          {loading ? 'Saving...' : 'Save Profile'}
        </button>
      </form>
    </div>
  )
}
