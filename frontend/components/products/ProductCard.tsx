import Link from 'next/link'
import Image from 'next/image'
import { Product } from '@/types/product'

export default function ProductCard({ product }: { product: Product }) {
  const priceDisplay = product.price_min
    ? product.price_max && product.price_max !== product.price_min
      ? `Rs. ${product.price_min} – ${product.price_max}/${product.unit}`
      : `Rs. ${product.price_min}/${product.unit}`
    : 'Price on request'

  return (
    <Link href={`/products/${product.slug}`} className="block bg-white border border-gray-200 rounded-xl overflow-hidden hover:shadow-md transition-shadow">
      <div className="aspect-square bg-gray-100 relative">
        {product.images?.[0] ? (
          <Image src={product.images[0]} alt={product.name} fill className="object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400 text-sm">No image</div>
        )}
        {product.is_featured && (
          <span className="absolute top-2 left-2 bg-amber-500 text-white text-xs px-2 py-0.5 rounded-full">Featured</span>
        )}
      </div>
      <div className="p-3">
        <h3 className="font-medium text-gray-900 text-sm line-clamp-2">{product.name}</h3>
        <p className="text-blue-600 font-semibold text-sm mt-1">{priceDisplay}</p>
        <p className="text-gray-500 text-xs mt-1">MOQ: {product.moq} {product.unit}</p>
        {product.views > 100 && (
          <span className="text-xs text-gray-400">{product.views} views</span>
        )}
      </div>
    </Link>
  )
}
