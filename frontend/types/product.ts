export interface Product {
  id: number
  name: string
  slug: string
  description: string
  unit: string
  moq: number
  price_min: number | null
  price_max: number | null
  images: string[]
  tags: string[] | null
  specifications: Record<string, string> | null
  is_featured: boolean
  status: string
  views: number
  inquiry_count: number
  company_id: number
  category_id: number
}

export interface Company {
  id: number
  name: string
  slug: string
  city: string
  state: string
  category: string
  phone: string | null
  description: string | null
  logo_url: string | null
  is_verified: boolean
  year_established: number | null
  employee_count: string | null
  total_leads: number
  website: string | null
}

export interface Category {
  id: number
  name: string
  slug: string
  parent_id: number | null
  icon_url: string | null
  product_count: number
}
