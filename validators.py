def is_non_empty_string(value):
    return isinstance(value, str) and len(value) > 0
    # Fix 1


def find_product_by_id(products, product_id):
    for product in products:
        if product["id"] == product_id:
            return product
    return None


def find_customer_by_id(customers, customer_id):
    for customer in customers:
        if customer["id"] == customer_id:
            return customer
    return None


def validate_order(order, products, customers):
    errors = []

    if "id" not in order:
        errors.append("Order is missing an id")

    if not is_non_empty_string(order.get("customer_id")):
        errors.append("Order is missing a customer id")

    customer = find_customer_by_id(customers, order.get("customer_id"))
    if customer is None:
        errors.append("Customer does not exist")

    items = order.get("items")

    if not isinstance(items, list) or len(items) == 0:
        errors.append("Order must contain at least one item")
        items = []

    requested_quantities = {}

    for item in items:
        product = find_product_by_id(products, item.get("product_id"))

        if product is None:
            errors.append(f"Product does not exist: {item.get('product_id')}")
            continue

        quantity = item.get("quantity")
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            errors.append(f"Quantity must be a positive integer for {product['name']}")
            # Fix 2

        if type(quantity) is int and quantity > 0:
            requested_quantities[product["id"]] = (
                requested_quantities.get(product["id"], 0) + quantity
            )

    for product_id, requested in requested_quantities.items():
        product = find_product_by_id(products, product_id)
        if requested > product["stock"]:
            errors.append(f"Not enough inventory for {product['name']}")

    return errors