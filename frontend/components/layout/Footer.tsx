import Link from 'next/link'

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300 py-12 mt-16">
      <div className="max-w-7xl mx-auto px-4 grid grid-cols-1 md:grid-cols-4 gap-8">
        <div>
          <h3 className="text-white font-bold text-lg mb-3">YourMarket</h3>
          <p className="text-sm">India&apos;s affordable B2B marketplace for SMEs, manufacturers and wholesalers.</p>
        </div>
        <div>
          <h4 className="text-white font-semibold mb-3">Categories</h4>
          <ul className="space-y-2 text-sm">
            <li><Link href="/category/textiles" className="hover:text-white">Textiles</Link></li>
            <li><Link href="/category/machinery" className="hover:text-white">Machinery</Link></li>
            <li><Link href="/category/fmcg" className="hover:text-white">FMCG</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="text-white font-semibold mb-3">For Sellers</h4>
          <ul className="space-y-2 text-sm">
            <li><Link href="/register" className="hover:text-white">List Your Products</Link></li>
            <li><Link href="/seller/subscription" className="hover:text-white">Pricing Plans</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="text-white font-semibold mb-3">Contact</h4>
          <p className="text-sm">Halvad, Gujarat, India</p>
          <p className="text-sm mt-1">support@yourdomain.in</p>
        </div>
      </div>
      <div className="text-center text-sm text-gray-500 mt-8">
        © {new Date().getFullYear()} YourMarket. All rights reserved.
      </div>
    </footer>
  )
}
