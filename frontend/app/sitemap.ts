import { MetadataRoute } from 'next'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000'
const BASE_URL = 'https://yourdomain.in'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const routes: MetadataRoute.Sitemap = [
    { url: BASE_URL, lastModified: new Date(), changeFrequency: 'daily', priority: 1.0 },
    { url: `${BASE_URL}/products`, lastModified: new Date(), changeFrequency: 'hourly', priority: 0.9 },
  ]

  try {
    const [productsRes, companiesRes, categoriesRes] = await Promise.all([
      fetch(`${API_URL}/api/sitemap/products`).then(r => r.json()),
      fetch(`${API_URL}/api/sitemap/companies`).then(r => r.json()),
      fetch(`${API_URL}/api/sitemap/categories`).then(r => r.json()),
    ])

    ;(productsRes.data || []).forEach(({ slug, updated_at }: { slug: string; updated_at: string }) => {
      routes.push({ url: `${BASE_URL}/products/${slug}`, lastModified: new Date(updated_at), changeFrequency: 'daily', priority: 0.7 })
    })
    ;(companiesRes.data || []).forEach(({ slug, updated_at }: { slug: string; updated_at: string }) => {
      routes.push({ url: `${BASE_URL}/companies/${slug}`, lastModified: new Date(updated_at), changeFrequency: 'weekly', priority: 0.8 })
    })
    ;(categoriesRes.data || []).forEach(({ slug }: { slug: string }) => {
      routes.push({ url: `${BASE_URL}/category/${slug}`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 })
    })
  } catch { /* continue with static routes */ }

  return routes
}
