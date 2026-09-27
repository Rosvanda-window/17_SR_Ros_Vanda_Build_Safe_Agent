# Practice data stored in memory.
PRODUCTS = {
    1: {"name": "Dell Laptop", "stock": 0},
    2: {"name": "Lenovo Laptop", "stock": 5},
    3: {"name": "Wireless Mouse", "stock": 12},
}


def search_products(keyword: str) -> dict:
    """Find products whose names contain the keyword."""
    keyword = keyword.strip().lower()

    if not keyword:
        return {"ok": False, "error": "Keyword cannot be empty."}

    matches = []

    for product_id, product in PRODUCTS.items():
        if keyword in product["name"].lower():
            matches.append({
                "id": product_id,
                "name": product["name"],
            })

    return {"ok": True, "products": matches}


def check_stock(product_id: int) -> dict:
    """Return the stock quantity of one product."""
    product = PRODUCTS.get(product_id)

    if product is None:
        return {"ok": False, "error": "Product not found."}

    return {
        "ok": True,
        "id": product_id,
        "name": product["name"],
        "stock": product["stock"],
        "available": product["stock"] > 0,
    }


def delete_product(product_id: int) -> dict:
    """Remove one product from the practice data."""
    product = PRODUCTS.get(product_id)

    if product is None:
        return {"ok": False, "error": "Product not found."}

    del PRODUCTS[product_id]

    return {
        "ok": True,
        "message": f"Deleted {product['name']}.",
    }