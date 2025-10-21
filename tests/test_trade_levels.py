import unittest
from ai_trading_bot import calculate_trade_levels


class TestCalculateTradeLevels(unittest.TestCase):
    def test_buy(self):
        price = 100.0
        tp, sl = calculate_trade_levels(price, "buy", 0.02, 0.01)
        self.assertAlmostEqual(tp, 102.0)
        self.assertAlmostEqual(sl, 99.0)

    def test_sell(self):
        price = 200.0
        tp, sl = calculate_trade_levels(price, "sell", 0.03, 0.015)
        self.assertAlmostEqual(tp, 194.0)
        self.assertAlmostEqual(sl, 203.0)

    def test_hold(self):
        price = 50.0
        tp, sl = calculate_trade_levels(price, "hold", 0.05, 0.02)
        self.assertEqual(tp, price)
        self.assertEqual(sl, price)


if __name__ == "__main__":
    unittest.main()
