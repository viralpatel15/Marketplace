'use client'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { api } from '@/lib/api'

const schema = z.object({
  quantity: z.coerce.number().min(1).optional(),
  message: z.string().max(500).optional(),
})
type FormData = z.infer<typeof schema>

export default function InquiryForm({ productId }: { productId: number }) {
  const [sent, setSent] = useState(false)
  const [error, setError] = useState('')
  const { register, handleSubmit, formState: { isSubmitting } } = useForm<FormData>({ resolver: zodResolver(schema) })

  const isLoggedIn = typeof window !== 'undefined' && !!localStorage.getItem('access_token')

  if (!isLoggedIn) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 text-center">
        <p className="text-gray-700 mb-4">Login to send inquiry and view seller contact details</p>
        <a href="/login" className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700">Login to Send Inquiry</a>
      </div>
    )
  }

  if (sent) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-xl p-6 text-center">
        <p className="text-green-700 font-medium">Inquiry sent! The seller will contact you soon.</p>
      </div>
    )
  }

  const onSubmit = async (data: FormData) => {
    try {
      await api.post('/api/inquiries', { product_id: productId, ...data })
      setSent(true)
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } }
      setError(e.response?.data?.detail || 'Failed to send inquiry')
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="bg-gray-50 border border-gray-200 rounded-xl p-6">
      <h3 className="font-semibold text-gray-900 mb-4">Send Inquiry to Seller</h3>
      <div className="mb-4">
        <label className="text-sm font-medium text-gray-700 block mb-1">Quantity Required</label>
        <input {...register('quantity')} type="number" placeholder="e.g. 100" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500" />
      </div>
      <div className="mb-4">
        <label className="text-sm font-medium text-gray-700 block mb-1">Your Message (optional)</label>
        <textarea {...register('message')} rows={3} placeholder="Describe your requirement..." className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500" />
      </div>
      {error && <p className="text-red-600 text-sm mb-3">{error}</p>}
      <button type="submit" disabled={isSubmitting} className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-60">
        {isSubmitting ? 'Sending...' : 'Send Inquiry'}
      </button>
    </form>
  )
}
