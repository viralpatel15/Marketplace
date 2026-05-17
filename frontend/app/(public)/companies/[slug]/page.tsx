import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import Image from 'next/image'
import Link from 'next/link'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000'

async function fetchCompany(slug: string) {
  try {
    const res = await fetch(`${API_URL}/api/companies/${slug}`, { next: { revalidate: 3600 } })
    return res.ok ? (await res.json()).data : null
  } catch { return null }
}

export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const company = await fetchCompany(params.slug)
  if (!company) return { title: 'Company Not Found' }
  return {
    title: `${company.name} - ${company.category} Supplier in ${company.city}`,
    description: company.description?.slice(0, 160) || `Find ${company.category} products from ${company.name} in ${company.city}.`,
  }
}

export default async function CompanyPage({ params }: { params: { slug: string } }) {
  const company = await fetchCompany(params.slug)
  if (!company) notFound()

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 mb-6">
        <div className="flex items-start gap-6">
          <div className="w-20 h-20 bg-gray-100 rounded-xl overflow-hidden relative shrink-0">
            {company.logo_url ? (
              <Image src={company.logo_url} alt={company.name} fill className="object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-2xl font-bold text-gray-400">
                {company.name[0]}
              </div>
            )}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-bold text-gray-900">{company.name}</h1>
              {company.is_verified && (
                <span className="bg-green-100 text-green-700 text-xs font-semibold px-2 py-0.5 rounded-full">GST Verified</span>
              )}
            </div>
            <p className="text-gray-600 text-sm mb-2">{company.category} · {company.city}, {company.state}</p>
            {company.year_established && <p className="text-gray-500 text-sm">Est. {company.year_established}</p>}
          </div>
        </div>

        {company.description && (
          <p className="text-gray-700 mt-4 text-sm leading-relaxed">{company.description}</p>
        )}

        <div className="mt-4 pt-4 border-t border-gray-100 flex gap-6 text-sm text-gray-600">
          {company.phone ? (
            <span>📞 {company.phone}</span>
          ) : (
            <Link href="/login" className="text-blue-600">Login to view contact</Link>
          )}
          {company.website && <a href={company.website} target="_blank" rel="noopener noreferrer" className="text-blue-600">🌐 Website</a>}
          <span>📦 {company.total_leads}+ leads received</span>
        </div>
      </div>

      {/* Products */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Products by {company.name}</h2>
        <Link href={`/products?company_id=${company.id}`} className="text-sm text-blue-600 hover:underline">View all products →</Link>
      </div>
    </div>
  )
}
