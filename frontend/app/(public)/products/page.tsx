import type { Metadata } from 'next'
import Link from 'next/link'
import ProductCard from '@/components/products/ProductCard'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000'

interface SearchParams {
  q?: string; category_id?: string; city?: string; price_min?: string; price_max?: string
  is_featured?: string; page?: string; sort?: string
}

export async function generateMetadata({ searchParams }: { searchParams: SearchParams }): Promise<Metadata> {
  const parts = []
  if (searchParams.q) parts.push(searchParams.q)
  if (searchParams.city) parts.push(`in ${searchParams.city}`)
  const title = parts.length ? `${parts.join(' ')} - Suppliers & Products` : 'Browse All Products'
  return { title, description: `Find verified ${title} on YourMarket. Compare prices, MOQ and suppliers across India.` }
}

export default async function ProductsPage({ searchParams }: { searchParams: SearchParams }) {
  const params = new URLSearchParams()
  if (searchParams.q) params.set('q', searchParams.q)
  if (searchParams.category_id) params.set('category_id', searchParams.category_id)
  if (searchParams.city) params.set('city', searchParams.city)
  if (searchParams.page) params.set('page', searchParams.page)

  const endpoint = searchParams.q
    ? `${API_URL}/api/products/search?${params}`
    : `${API_URL}/api/products?${params}`

  let products: { id: number; slug: string; name: string; price_min: number | null; price_max: number | null; unit: string; moq: number; images: string[]; is_featured: boolean; views: number; inquiry_count: number; status: string; company_id: number; category_id: number; description: string; tags: string[] | null; specifications: Record<string, string> | null }[] = []
  let total = 0
  try {
    const res = await fetch(endpoint, { next: { revalidate: 300 } })
    const data = await res.json()
    products = data.data || []
    total = data.meta?.total || 0
  } catch { /* ignore */ }

  const categoriesRes = await fetch(`${API_URL}/api/categories`, { next: { revalidate: 3600 } }).catch(() => null)
  const categories = categoriesRes ? (await categoriesRes.json()).data || [] : []

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex gap-8">
        {/* Filters sidebar */}
        <aside className="w-64 shrink-0 hidden md:block">
          <div className="bg-white border border-gray-200 rounded-xl p-4">
            <h3 className="font-semibold text-gray-900 mb-4">Filters</h3>
            <form method="GET">
              {searchParams.q && <input type="hidden" name="q" value={searchParams.q} />}
              <div className="mb-4">
                <label className="text-sm font-medium text-gray-700 block mb-2">Category</label>
                <select name="category_id" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                  <option value="">All Categories</option>
                  {categories.filter((c: { parent_id: number | null }) => !c.parent_id).map((c: { id: number; name: string }) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
              <div className="mb-4">
                <label className="text-sm font-medium text-gray-700 block mb-2">City</label>
                <input name="city" defaultValue={searchParams.city} placeholder="e.g. Surat" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
              </div>
              <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded-lg text-sm font-medium">Apply Filters</button>
            </form>
          </div>
        </aside>

        {/* Results */}
        <div className="flex-1">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-xl font-bold text-gray-900">
              {searchParams.q ? `Results for "${searchParams.q}"` : 'All Products'}
              <span className="text-sm font-normal text-gray-500 ml-2">({total} found)</span>
            </h1>
          </div>
          {products.length === 0 ? (
            <div className="text-center py-16 text-gray-500">No products found. Try a different search.</div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {products.map((p) => <ProductCard key={p.id} product={p} />)}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
