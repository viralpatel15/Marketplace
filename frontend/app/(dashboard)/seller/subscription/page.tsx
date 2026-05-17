'use client'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

interface Plan {
  id: number; name: string; price_monthly: number; max_products: number
  leads_per_month: number; has_analytics: boolean; has_whatsapp: boolean; support_level: string
}

export default function SubscriptionPage() {
  const [plans, setPlans] = useState<Plan[]>([])
  const [status, setStatus] = useState<{ plan: string; status: string } | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.get('/api/plans').then(r => setPlans(r.data.data))
    api.get('/api/subscribe/status').then(r => setStatus(r.data.data)).catch(() => {})
  }, [])

  const subscribe = async (planId: number) => {
    setLoading(true)
    try {
      const res = await api.post('/api/subscribe', { plan_id: planId })
      const { checkout_url } = res.data.data
      if (checkout_url) window.open(checkout_url, '_blank')
    } catch (err: unknown) {
      alert((err as { response?: { data?: { detail?: string } } }).response?.data?.detail || 'Failed to create subscription')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Subscription Plans</h1>
      {status && <p className="text-gray-600 mb-8">Current plan: <strong>{status.plan}</strong> ({status.status})</p>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {plans.map((plan) => (
          <div key={plan.id} className={`bg-white border rounded-2xl p-6 ${plan.name === 'Pro' ? 'border-blue-500 shadow-md' : 'border-gray-200'}`}>
            {plan.name === 'Pro' && <div className="text-blue-600 text-xs font-bold mb-2 uppercase tracking-wide">Most Popular</div>}
            <h3 className="text-xl font-bold text-gray-900">{plan.name}</h3>
            <div className="my-4">
              <span className="text-3xl font-bold text-gray-900">₹{plan.price_monthly}</span>
              <span className="text-gray-500 text-sm">/month</span>
            </div>
            <ul className="space-y-2 text-sm text-gray-700 mb-6">
              <li>📦 {plan.max_products === -1 ? 'Unlimited' : plan.max_products} products</li>
              <li>📋 {plan.leads_per_month === -1 ? 'Unlimited' : plan.leads_per_month} leads/month</li>
              {plan.has_analytics && <li>📊 Analytics dashboard</li>}
              {plan.has_whatsapp && <li>💬 WhatsApp alerts</li>}
              <li>🛠️ {plan.support_level} support</li>
            </ul>
            {plan.price_monthly > 0 && (
              <button onClick={() => subscribe(plan.id)} disabled={loading} className="w-full bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-60 text-sm">
                {loading ? 'Processing...' : `Upgrade to ${plan.name}`}
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
