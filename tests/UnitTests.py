from coverage import coverage

cov = coverage()
cov.start()
#################################################################################################
################################Coverage_START#####################################################
import unittest
from bm35_tests import bm35TestCase
from CountsPettioner_tests import CountsPettionerTestCase
from Reader_tests import ReaderTestCase

def bm35_suite():
	return unittest.TestLoader().loadTestsFromTestCase(bm35TestCase)

def CountsPettioner_suite():
	return unittest.TestLoader().loadTestsFromTestCase(CountsPettionerTestCase)

def Reader_suite():
	return unittest.TestLoader().loadTestsFromTestCase(ReaderTestCase)

if __name__ == '__main__':
	#  TODO add arguments wih argparse which will allow us to test different units.
	allTests=unittest.TestSuite()
	allTests.addTests(bm35_suite())
	allTests.addTests(CountsPettioner_suite())
	allTests.addTests(Reader_suite())
	
	unittest.TextTestRunner(verbosity=2).run(allTests)
#################################################################################################
################################Coverage_END#####################################################
cov.stop()
cov.html_report(directory='covhtml',omit=['*test*','/usr/*'])
