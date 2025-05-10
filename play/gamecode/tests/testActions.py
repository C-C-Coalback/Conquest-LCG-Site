import unittest


class ActionsTest(unittest.IsolatedAsyncioTestCase):
    async def test_setup(self):
        self.assertEqual(True, True)


if __name__ == "__main__":
    unittest.main()
