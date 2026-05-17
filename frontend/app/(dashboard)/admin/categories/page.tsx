'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

interface Category {
  id: number; name: string; slug: string; parent_id: number | null; product_count: number; is_active: boolean
}

export default function AdminCategoriesPage() {
  const [categories, setCategories] = useState<Category[]>([])
  const [newCat, setNewCat] = useState({ name: '', slug: '', parent_id: '' })
  const [adding, setAdding] = useState(false)

  useEffect(() => {
    api.get('/api/categories').then(r => setCategories(r.data.data))
  }, [])

  const addCategory = async (e: React.FormEvent) => {
    e.preventDefault()
    setAdding(true)
    try {
      const res = await api.post('/api/admin/categories', { ...newCat, parent_id: newCat.parent_id ? parseInt(newCat.parent_id) : null })
      setCategories([...categories, res.data.data])
      setNewCat({ name: '', slug: '', parent_id: '' })
    } finally {
      setAdding(false)
    }
  }

  const topLevel = categories.filter(c => !c.parent_id)

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Category Management</h1>

      <form onSubmit={addCategory} className="bg-white border border-gray-200 rounded-xl p-5 mb-6">
        <h3 className="font-semibold text-gray-900 mb-4">Add Category</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input required value={newCat.name} onChange={e => setNewCat(f => ({ ...f, name: e.target.value, slug: e.target.value.toLowerCase().replace(/\s+/g, '-') }))} placeholder="Category name" className="border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          <input required value={newCat.slug} onChange={e => setNewCat(f => ({ ...f, slug: e.target.value }))} placeholder="url-slug" className="border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          <select value={newCat.parent_id} onChange={e => setNewCat(f => ({ ...f, parent_id: e.target.value }))} className="border border-gray-300 rounded-lg px-3 py-2 text-sm">
            <option value="">Top-level category</option>
            {topLevel.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
        <button type="submit" disabled={adding} className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-60">
          {adding ? 'Adding...' : 'Add Category'}
        </button>
      </form>

      <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-600 font-medium">
            <tr>
              <th className="text-left px-4 py-3">Name</th>
              <th className="text-left px-4 py-3">Slug</th>
              <th className="text-left px-4 py-3">Parent</th>
              <th className="text-left px-4 py-3">Products</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {categories.map((c) => {
              const parent = categories.find(p => p.id === c.parent_id)
              return (
                <tr key={c.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{c.parent_id ? '↳ ' : ''}{c.name}</td>
                  <td className="px-4 py-3 text-gray-500 font-mono text-xs">{c.slug}</td>
                  <td className="px-4 py-3 text-gray-600">{parent?.name || '—'}</td>
                  <td className="px-4 py-3 text-gray-600">{c.product_count}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
