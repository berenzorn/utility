import unittest
import hashgen as hg


class HashgenTest(unittest.TestCase):

    def test_hashgen_file(self):
        self.assertEqual(hg.hashgen_file('test', 100, True), '9e4bdc87f1408f4e2444e8d5b4461813e939095f')
        self.assertEqual(hg.hashgen_file('test', -1, True), '9e4bdc87f1408f4e2444e8d5b4461813e939095f')
        self.assertEqual(hg.hashgen_file('test', 0, True), '9e4bdc87f1408f4e2444e8d5b4461813e939095f')
        self.assertEqual(hg.hashgen_file('tst', 0, True), False)

    def test_file_array(self):
        result = hg.file_array('.', False)
        self.assertEqual(type(result), list)
        result = hg.file_array('.', True)
        self.assertEqual(type(result), list)
        self.assertEqual(hg.file_array(',', False), False)
        self.assertEqual(hg.file_array(',', True), False)

    def test_new_files(self):
        result = hg.new_files('.', '.')
        self.assertEqual(type(result), tuple)
        self.assertEqual(hg.new_files(';', ';'), False)


if __name__ == '__main__':
    unittest.main()
