'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { api } from '@/lib/api'

interface Category { id: number; name: string; parent_id: number | null }

export default function NewProductPage() {
  const router = useRouter()
  const [categories, setCategories] = useState<Category[]>([])
  const [form, setForm] = useState({ name: '', category_id: '', description: '', unit: 'piece', moq: 1, price_min: '', price_max: '', tags: '' })
  const [images, setImages] = useState<File[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [productId, setProductId] = useState<number | null>(null)
  const [step, setStep] = useState(1)

  useEffect(() => {
    api.get('/api/categories').then(r => setCategories(r.data.data))
  }, [])

  const createProduct = async () => {
    setLoading(true)
    setError('')
    try {
      const payload = {
        name: form.name, category_id: parseInt(form.category_id), description: form.description,
        unit: form.unit, moq: form.moq,
        price_min: form.price_min ? parseFloat(form.price_min) : null,
        price_max: form.price_max ? parseFloat(form.price_max) : null,
        tags: form.tags ? form.tags.split(',').map(t => t.trim()).filter(Boolean) : null,
      }
      const res = await api.post('/api/products', payload)
      setProductId(res.data.data.id)
      setStep(3)
    } catch (err: unknown) {
      setError((err as { response?: { data?: { detail?: string } } }).response?.data?.detail || 'Failed to create product')
    } finally {
      setLoading(false)
    }
  }

  const uploadImages = async () => {
    if (!productId || images.length === 0) { router.push('/seller/products'); return }
    setLoading(true)
    try {
      const fd = new FormData()
      images.forEach(f => fd.append('files', f))
      await api.post(`/api/products/${productId}/images`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      router.push('/seller/products')
    } catch {
      setError('Product created but image upload failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Add New Product</h1>
      <div className="flex gap-2 mb-8">
        {['Details', 'Pricing', 'Images'].map((s, i) => (
          <div key={s} className={`flex-1 text-center py-2 text-sm font-medium rounded-lg ${step === i + 1 ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-500'}`}>{s}</div>
        ))}
      </div>

      <div className="bg-white border border-gray-200 rounded-xl p-6">
        {step === 1 && (
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">Product Name *</label>
              <input value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-500" />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">Category *</label>
              <select value={form.category_id} onChange={e => setForm(f => ({ ...f, category_id: e.target.value }))} className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm">
                <option value="">Select category</option>
                {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">Description *</label>
              <textarea value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} rows={4} className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-500" />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-1">Tags (comma separated)</label>
              <input value={form.tags} onChange={e => setForm(f => ({ ...f, tags: e.target.value }))} placeholder="cotton, fabric, woven" className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm" />
            </div>
            <button onClick={() => setStep(2)} disabled={!form.name || !form.category_id || !form.description} className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-60">Next: Pricing</button>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-700 block mb-1">Min Price (Rs.)</label>
                <input type="number" value={form.price_min} onChange={e => setForm(f => ({ ...f, price_min: e.target.value }))} className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm" />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700 block mb-1">Max Price (Rs.)</label>
                <input type="number" value={form.price_max} onChange={e => setForm(f => ({ ...f, price_max: e.target.value }))} className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-700 block mb-1">Unit</label>
                <select value={form.unit} onChange={e => setForm(f => ({ ...f, unit: e.target.value }))} className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm">
                  {['piece', 'kg', 'meter', 'ton', 'box', 'liter', 'set'].map(u => <option key={u}>{u}</option>)}
                </select>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700 block mb-1">Min Order Qty</label>
                <input type="number" value={form.moq} onChange={e => setForm(f => ({ ...f, moq: parseInt(e.target.value) || 1 }))} className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm" />
              </div>
            </div>
            {error && <p className="text-red-600 text-sm">{error}</p>}
            <button onClick={createProduct} disabled={loading} className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-60">
              {loading ? 'Creating...' : 'Create Product & Add Images'}
            </button>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-700 block mb-2">Upload Images (max 10)</label>
              <input type="file" accept="image/*" multiple onChange={e => setImages(Array.from(e.target.files || []).slice(0, 10))} className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm" />
              {images.length > 0 && <p className="text-sm text-gray-500 mt-1">{images.length} image(s) selected</p>}
            </div>
            {error && <p className="text-red-600 text-sm">{error}</p>}
            <button onClick={uploadImages} disabled={loading} className="w-full bg-green-600 text-white py-2.5 rounded-lg font-semibold hover:bg-green-700 disabled:opacity-60">
              {loading ? 'Uploading...' : images.length ? 'Upload & Finish' : 'Skip & Finish'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
