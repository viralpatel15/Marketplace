import type { Metadata } from 'next'
import './globals.css'
import Navbar from '@/components/layout/Navbar'
import Footer from '@/components/layout/Footer'

export const metadata: Metadata = {
  metadataBase: new URL('https://yourdomain.in'),
  title: { default: 'YourMarket - B2B Marketplace India | Find Verified Suppliers', template: '%s | YourMarket' },
  description: 'Find verified B2B suppliers, manufacturers and wholesalers across India. Cheaper than IndiaMART, easier to use.',
  openGraph: { siteName: 'YourMarket', type: 'website', locale: 'en_IN' },
  twitter: { card: 'summary_large_image' },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        <main className="min-h-screen">{children}</main>
        <Footer />
      </body>
    </html>
  )
}
