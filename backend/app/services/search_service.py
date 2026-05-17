import meilisearch
from app.core.config import settings

client = meilisearch.Client(settings.MEILI_URL, settings.MEILI_KEY)
index = client.index("products")


def configure_index():
    index.update_settings({
        "searchableAttributes": ["name", "description", "tags", "company_name"],
        "filterableAttributes": ["category_id", "city", "price_min", "price_max", "is_featured", "status"],
        "sortableAttributes": ["views", "created_at", "price_min"],
        "rankingRules": ["words", "typo", "proximity", "attribute", "sort", "exactness"],
    })


def index_product(product: dict):
    index.add_documents([{
        "id": product["id"],
        "name": product["name"],
        "description": product["description"],
        "category_id": product["category_id"],
        "city": product.get("city", ""),
        "price_min": float(product["price_min"]) if product.get("price_min") else None,
        "price_max": float(product["price_max"]) if product.get("price_max") else None,
        "tags": product.get("tags", []),
        "is_featured": product.get("is_featured", False),
        "status": product.get("status", "active"),
        "company_name": product.get("company_name", ""),
    }])


def delete_product(product_id: int):
    index.delete_document(product_id)


def search_products(q: str, filters: dict, sort: str = "views", order: str = "desc", page: int = 1, limit: int = 20):
    filter_parts = []
    if filters.get("category_id"):
        filter_parts.append(f"category_id = {filters['category_id']}")
    if filters.get("city"):
        filter_parts.append(f'city = "{filters["city"]}"')
    if filters.get("price_min"):
        filter_parts.append(f"price_min >= {filters['price_min']}")
    if filters.get("price_max"):
        filter_parts.append(f"price_max <= {filters['price_max']}")
    if filters.get("is_featured") is not None:
        filter_parts.append(f"is_featured = {str(filters['is_featured']).lower()}")
    filter_parts.append('status = "active"')

    sort_field = sort if sort in ["views", "price_min"] else "views"
    return index.search(q or "", {
        "filter": " AND ".join(filter_parts),
        "limit": limit,
        "offset": (page - 1) * limit,
        "sort": [f"is_featured:desc", f"{sort_field}:{order}"],
    })
