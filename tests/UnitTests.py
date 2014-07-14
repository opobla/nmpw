import unittest
from bm35_tests import bm35TestCase

def bm35_suite():
	return unittest.TestLoader().loadTestsFromTestCase(bm35TestCase)


if __name__ == '__main__':
	#  TODO add arguments wih argparse which will allow us to test different units.
	allTests=unittest.TestSuite()
	allTests.addTests(bm35_suite())

	
	unittest.TextTestRunner(verbosity=2).run(allTests)
