import unittest
from copy import deepcopy
from unittest.mock import patch

from data import get_customers, get_orders, get_products, get_tax_rates
from orders import process_order
from reports import revenue_summary


class OrderRejectionTests(unittest.TestCase):
    def assert_rejected(self, order):
        products = get_products()
        original = deepcopy(products)
        result = process_order(order, products, get_customers(), get_tax_rates())
        self.assertFalse(result["valid"])
        self.assertTrue(result["errors"])
        self.assertEqual(products, original)
        for field in ("subtotal", "tax", "shipping", "total"):
            self.assertEqual(result[field], 0)
        self.assertTrue(all(value == 0 for value in result["discounts"].values()))
        self.assertEqual(revenue_summary([result])["total_revenue"], 0)
        return result

    def test_out_of_stock_order_is_atomic(self):
        self.assert_rejected(get_orders()[1])

    def test_missing_customer(self):
        order = get_orders()[0]
        order["customer_id"] = "UNKNOWN"
        self.assertEqual(self.assert_rejected(order)["customer"], "UNKNOWN")

    def test_missing_product(self):
        order = get_orders()[0]
        order["items"][1]["product_id"] = "UNKNOWN"
        self.assert_rejected(order)

    def test_missing_id(self):
        order = get_orders()[0]
        del order["id"]
        self.assertIsNone(self.assert_rejected(order)["order_id"])

    def test_missing_items(self):
        order = get_orders()[0]
        del order["items"]
        self.assert_rejected(order)

    def test_empty_items(self):
        order = get_orders()[0]
        order["items"] = []
        self.assert_rejected(order)

    def test_rejection_skips_calculations_and_inventory(self):
        names = ("calculate_subtotal", "apply_discounts", "calculate_tax",
                 "calculate_shipping", "reserve_inventory")
        from contextlib import ExitStack
        with ExitStack() as stack:
            mocks = [stack.enter_context(patch("orders." + name)) for name in names]
            self.assert_rejected(get_orders()[1])
            for mock in mocks:
                mock.assert_not_called()

    def test_valid_order_still_reserves_inventory(self):
        products = get_products()
        result = process_order(get_orders()[0], products, get_customers(), get_tax_rates())
        self.assertTrue(result["valid"])
        self.assertEqual(result["errors"], [])
        self.assertEqual(products[0]["stock"], 10)
        self.assertEqual(products[1]["stock"], 3)


if __name__ == "__main__":
    unittest.main()
