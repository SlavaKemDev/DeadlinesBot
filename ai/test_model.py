import unittest
from datetime import datetime, timedelta
import json
import os

from .model import Model


class TestModel(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        current_dir = os.path.dirname(__file__)
        texts_path = os.path.join(current_dir, "tests.json")

        with open(texts_path) as f:
            self.data = json.load(f)

        self.model = Model()

    async def test_simple(self):
        response = await self.model.get_deadlines(self.data['simple'], [])

        self.assertEqual(1, len(response))
        self.assertTrue("ИДЗ" in response[0][0])
        self.assertEqual(datetime.strptime("24.03.2025 23:00:00", "%d.%m.%Y %H:%M:%S"), response[0][1])

    async def test_reply(self):
        response = await self.model.get_deadlines(self.data['reply'], [("ИДЗ 4", datetime.strptime("21.05.2025 23:00:00", "%d.%m.%Y %H:%M:%S"))])

        self.assertEqual(1, len(response))
        self.assertTrue("ИДЗ" in response[0][0])
        self.assertEqual(datetime.strptime("25.05.2025 23:00:00", "%d.%m.%Y %H:%M:%S"), response[0][1])

    async def test_complex_date(self):
        response = await self.model.get_deadlines(self.data['complex_date'], [])

        self.assertEqual(1, len(response))
        self.assertEqual(datetime.strptime("20.04.2025 04:00:00", "%d.%m.%Y %H:%M:%S"), response[0][1])


if __name__ == '__main__':
    unittest.main()
