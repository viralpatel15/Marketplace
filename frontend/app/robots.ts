import { MetadataRoute } from 'next'

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: '*',
      allow: '/',
      disallow: ['/seller/', '/admin/', '/api/'],
    },
    sitemap: 'https://yourdomain.in/sitemap.xml',
  }
}
