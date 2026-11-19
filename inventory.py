def reserve_inventory(products, order):
    needed = {}
    for item in order["items"]:
        product = next((p for p in products if p["id"] == item["product_id"]), None)
        quantity = item.get("quantity")
        if product is None or not isinstance(quantity, int) or quantity <= 0:
            return False
        needed[item["product_id"]] = needed.get(item["product_id"], 0) + quantity

    for product_id, quantity in needed.items():
        product = next(p for p in products if p["id"] == product_id)
        if product["stock"] < quantity:
            return False

    for product_id, quantity in needed.items():
        product = next(p for p in products if p["id"] == product_id)
        product["stock"] -= quantity
    return True

def restock_product(products, product_id, amount):
    for product in products:
        if product["id"] == product_id:
            product["stock"] += amount
            return product
    return None
