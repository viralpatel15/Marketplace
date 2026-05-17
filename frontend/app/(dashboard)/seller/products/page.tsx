'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { api } from '@/lib/api'

interface Product {
  id: number; name: string; status: string; views: number; inquiry_count: number; images: string[]; price_min: number | null; unit: string
}

export default function SellerProductsPage() {
  const [products, setProducts] = useState<Product[]>([])
  const [total, setTotal] = useState(0)

  useEffect(() => {
    api.get('/api/products/my').then(r => {
      setProducts(r.data.data)
      setTotal(r.data.meta?.total || 0)
    })
  }, [])

  const deleteProduct = async (id: number) => {
    if (!confirm('Delete this product?')) return
    await api.delete(`/api/products/${id}`)
    setProducts(products.filter(p => p.id !== id))
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">My Products ({total})</h1>
        <Link href="/seller/products/new" className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700">+ Add Product</Link>
      </div>

      <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-600 font-medium">
            <tr>
              <th className="text-left px-4 py-3">Product</th>
              <th className="text-left px-4 py-3">Price</th>
              <th className="text-left px-4 py-3">Views</th>
              <th className="text-left px-4 py-3">Leads</th>
              <th className="text-left px-4 py-3">Status</th>
              <th className="text-left px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {products.map((p) => (
              <tr key={p.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    {p.images?.[0] && <img src={p.images[0]} alt={p.name} className="w-10 h-10 rounded-lg object-cover" />}
                    <span className="font-medium text-gray-900 line-clamp-1">{p.name}</span>
                  </div>
                </td>
                <td className="px-4 py-3 text-gray-600">{p.price_min ? `₹${p.price_min}/${p.unit}` : '—'}</td>
                <td className="px-4 py-3 text-gray-600">{p.views}</td>
                <td className="px-4 py-3 text-gray-600">{p.inquiry_count}</td>
                <td className="px-4 py-3">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${p.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>{p.status}</span>
                </td>
                <td className="px-4 py-3">
                  <button onClick={() => deleteProduct(p.id)} className="text-red-500 hover:text-red-700 text-xs">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {products.length === 0 && <div className="text-center py-12 text-gray-500">No products yet. <Link href="/seller/products/new" className="text-blue-600 hover:underline">Add your first product</Link></div>}
      </div>
    </div>
  )
}
