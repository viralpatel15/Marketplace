import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Image from 'next/image'
import Link from 'next/link'
import InquiryForm from '@/components/products/InquiryForm'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000'

async function fetchProduct(slug: string) {
  try {
    const res = await fetch(`${API_URL}/api/products/${slug}`, { next: { revalidate: 3600 } })
    if (!res.ok) return null
    return (await res.json()).data
  } catch { return null }
}

async function fetchCompany(id: number) {
  try {
    const res = await fetch(`${API_URL}/api/companies/by-id/${id}`, { next: { revalidate: 3600 } })
    return res.ok ? (await res.json()).data : null
  } catch { return null }
}

export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const product = await fetchProduct(params.slug)
  if (!product) return { title: 'Product Not Found' }
  return {
    title: `${product.name} Supplier | YourMarket`,
    description: product.description?.slice(0, 160),
    openGraph: { title: product.name, images: product.images?.[0] ? [product.images[0]] : [], type: 'website' },
  }
}

function ProductJsonLd({ product }: { product: { name: string; description: string; images: string[]; price_min: number | null; price_max: number | null } }) {
  const ld = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.name,
    description: product.description,
    image: product.images,
    offers: {
      '@type': 'AggregateOffer',
      lowPrice: product.price_min,
      highPrice: product.price_max,
      priceCurrency: 'INR',
    },
  }
  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(ld) }} />
}

export default async function ProductPage({ params }: { params: { slug: string } }) {
  const product = await fetchProduct(params.slug)
  if (!product) notFound()

  const priceDisplay = product.price_min
    ? product.price_max ? `Rs. ${product.price_min} – ${product.price_max}` : `Rs. ${product.price_min}`
    : 'Price on request'

  return (
    <>
      <ProductJsonLd product={product} />
      <div className="max-w-6xl mx-auto px-4 py-8">
        <nav className="text-sm text-gray-500 mb-6">
          <Link href="/">Home</Link> / <Link href="/products">Products</Link> / <span className="text-gray-900">{product.name}</span>
        </nav>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Images */}
          <div>
            <div className="aspect-square bg-gray-100 rounded-xl overflow-hidden relative mb-3">
              {product.images?.[0] ? (
                <Image src={product.images[0]} alt={product.name} fill className="object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-400">No image</div>
              )}
            </div>
            {product.images?.length > 1 && (
              <div className="flex gap-2">
                {product.images.slice(1, 5).map((img: string, i: number) => (
                  <div key={i} className="w-16 h-16 bg-gray-100 rounded-lg overflow-hidden relative">
                    <Image src={img} alt={`${product.name} ${i + 2}`} fill className="object-cover" />
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Details */}
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">{product.name}</h1>
            <p className="text-2xl font-bold text-blue-600 mb-1">{priceDisplay}<span className="text-base font-normal text-gray-500"> per {product.unit}</span></p>
            <p className="text-sm text-gray-600 mb-4">Minimum Order: {product.moq} {product.unit}</p>

            {product.tags?.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-4">
                {product.tags.map((tag: string) => (
                  <span key={tag} className="bg-gray-100 text-gray-600 text-xs px-3 py-1 rounded-full">{tag}</span>
                ))}
              </div>
            )}

            <div className="prose prose-sm text-gray-700 mb-6">
              <p>{product.description}</p>
            </div>

            {product.specifications && Object.keys(product.specifications).length > 0 && (
              <div className="mb-6">
                <h3 className="font-semibold text-gray-900 mb-2">Specifications</h3>
                <table className="w-full text-sm border-collapse">
                  {Object.entries(product.specifications).map(([k, v]) => (
                    <tr key={k} className="border-b border-gray-100">
                      <td className="py-1.5 text-gray-600 font-medium w-1/2">{k}</td>
                      <td className="py-1.5 text-gray-900">{String(v)}</td>
                    </tr>
                  ))}
                </table>
              </div>
            )}

            <InquiryForm productId={product.id} />
          </div>
        </div>
      </div>
    </>
  )
}
