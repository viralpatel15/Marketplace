import type { Metadata } from 'next'
import Link from 'next/link'
import ProductCard from '@/components/products/ProductCard'

export const metadata: Metadata = {
  title: 'YourMarket - B2B Marketplace India | Find Verified Suppliers',
  description: 'Connect with verified Indian manufacturers, wholesalers and suppliers. Cheaper than IndiaMART. Browse Textiles, Machinery, FMCG and more.',
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000'

async function fetchFeatured() {
  try {
    const res = await fetch(`${API_URL}/api/products/featured`, { next: { revalidate: 3600 } })
    const data = await res.json()
    return data.data || []
  } catch { return [] }
}

async function fetchCategories() {
  try {
    const res = await fetch(`${API_URL}/api/categories`, { next: { revalidate: 3600 } })
    const data = await res.json()
    return data.data || []
  } catch { return [] }
}

export default async function HomePage() {
  const [featured, categories] = await Promise.all([fetchFeatured(), fetchCategories()])

  return (
    <div>
      {/* Hero */}
      <section className="bg-gradient-to-br from-blue-600 to-blue-800 text-white py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">Find Verified Indian Suppliers</h1>
          <p className="text-blue-100 text-lg mb-8">Cheaper than IndiaMART. Easier to use. Mobile-first.</p>
          <form action="/products" method="GET" className="flex gap-2 max-w-xl mx-auto">
            <input name="q" placeholder="Search cotton fabric, CNC machines, packaging..." className="flex-1 rounded-lg px-4 py-3 text-gray-900 text-sm focus:outline-none" />
            <button type="submit" className="bg-amber-500 hover:bg-amber-600 px-6 py-3 rounded-lg font-semibold text-sm">Search</button>
          </form>
        </div>
      </section>

      {/* Categories */}
      {categories.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 py-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Browse by Category</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {categories.slice(0, 8).map((cat: { id: number; slug: string; icon_url: string | null; name: string; product_count: number }) => (
              <Link key={cat.id} href={`/category/${cat.slug}`} className="bg-white border border-gray-200 rounded-xl p-4 text-center hover:shadow-md transition-shadow">
                {cat.icon_url && <img src={cat.icon_url} alt={cat.name} className="w-10 h-10 mx-auto mb-2" />}
                <p className="text-sm font-medium text-gray-900">{cat.name}</p>
                <p className="text-xs text-gray-500">{cat.product_count} products</p>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Featured Products */}
      {featured.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Featured Products</h2>
            <Link href="/products?is_featured=true" className="text-blue-600 text-sm hover:underline">View all</Link>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {featured.map((p: { id: number; slug: string; name: string; price_min: number | null; price_max: number | null; unit: string; moq: number; images: string[]; is_featured: boolean; views: number; inquiry_count: number; status: string; company_id: number; category_id: number; description: string; tags: string[] | null; specifications: Record<string, string> | null }) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        </section>
      )}

      {/* How it works */}
      <section className="bg-gray-50 py-16 px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 text-center mb-10">How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { step: '1', title: 'Search Products', desc: 'Browse thousands of verified suppliers across India.' },
              { step: '2', title: 'Send Inquiry', desc: 'Contact sellers directly with your requirements.' },
              { step: '3', title: 'Close the Deal', desc: 'Get quotes, negotiate, and finalize your order.' },
            ].map((item) => (
              <div key={item.step} className="text-center">
                <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">{item.step}</div>
                <h3 className="font-semibold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-gray-600 text-sm">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Seller CTA */}
      <section className="max-w-7xl mx-auto px-4 py-16 text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">List Your Products Today</h2>
        <p className="text-gray-600 mb-8">Start free. No setup fees. We help you list your products.</p>
        <Link href="/register?role=seller" className="bg-blue-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-blue-700">
          Get Started Free
        </Link>
      </section>
    </div>
  )
}
