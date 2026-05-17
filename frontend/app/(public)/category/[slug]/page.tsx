import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import ProductCard from '@/components/products/ProductCard'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000'

async function fetchCategory(slug: string) {
  try {
    const res = await fetch(`${API_URL}/api/categories/${slug}`, { next: { revalidate: 3600 } })
    return res.ok ? (await res.json()).data : null
  } catch { return null }
}

async function fetchCategoryProducts(slug: string) {
  try {
    const res = await fetch(`${API_URL}/api/categories/${slug}/products?limit=20`, { next: { revalidate: 300 } })
    return res.ok ? (await res.json()) : { data: [], meta: { total: 0 } }
  } catch { return { data: [], meta: { total: 0 } } }
}

export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const category = await fetchCategory(params.slug)
  if (!category) return { title: 'Category Not Found' }
  return {
    title: `${category.name} Suppliers & Manufacturers in India`,
    description: `Find verified ${category.name} suppliers, manufacturers and wholesalers across India. Compare prices, MOQ and get quotes.`,
  }
}

export default async function CategoryPage({ params }: { params: { slug: string } }) {
  const [category, productsData] = await Promise.all([fetchCategory(params.slug), fetchCategoryProducts(params.slug)])
  if (!category) notFound()

  const products = productsData.data || []

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Hero */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-8 mb-8">
        <nav className="text-sm text-gray-500 mb-3">
          <Link href="/">Home</Link> / <Link href="/products">Products</Link> / <span className="text-gray-900">{category.name}</span>
        </nav>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{category.name} Suppliers in India</h1>
        <p className="text-gray-600">{category.description || `Find verified ${category.name} manufacturers, wholesalers and suppliers.`}</p>
      </div>

      {/* Subcategories */}
      {category.children?.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Sub-Categories</h2>
          <div className="flex flex-wrap gap-3">
            {category.children.map((child: { slug: string; name: string }) => (
              <Link key={child.slug} href={`/category/${child.slug}`} className="bg-white border border-gray-200 rounded-lg px-4 py-2 text-sm hover:border-blue-500 hover:text-blue-600">
                {child.name}
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Products */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">{category.name} Products</h2>
          <span className="text-sm text-gray-500">{productsData.meta?.total || 0} products</span>
        </div>
        {products.length === 0 ? (
          <div className="text-center py-16 text-gray-500">No products in this category yet.</div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {products.map((p: { id: number; slug: string; name: string; price_min: number | null; price_max: number | null; unit: string; moq: number; images: string[]; is_featured: boolean; views: number; inquiry_count: number; status: string; company_id: number; category_id: number; description: string; tags: string[] | null; specifications: Record<string, string> | null }) => <ProductCard key={p.id} product={p} />)}
          </div>
        )}
      </div>
    </div>
  )
}
