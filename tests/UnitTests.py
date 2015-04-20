from coverage import coverage

cov = coverage()
cov.start()
#################################################################################################
################################Coverage_START#####################################################
import unittest
from bm35_tests import bm35TestCase
#from CountsPettioner_tests import CountsPettionerTestCase
from FPGASerialReader_tests import ReaderTestCase
from SensorsManager_tests import SensorsManagerTestCase
from DBUpdater_tests import DBUpdaterTestCase
#from bbbDAQ_tests import bbbDAQTestCase

def bm35_suite():
	return unittest.TestLoader().loadTestsFromTestCase(bm35TestCase)

def SensorsManager_suite():
	return unittest.TestLoader().loadTestsFromTestCase(SensorsManagerTestCase)

def Reader_suite():
	return unittest.TestLoader().loadTestsFromTestCase(ReaderTestCase)

def DBUpdater_suite():
	return unittest.TestLoader().loadTestsFromTestCase(DBUpdaterTestCase)

"""
def CountsPettioner_suite():
	return unittest.TestLoader().loadTestsFromTestCase(CountsPettionerTestCase)

def bbbDAQ_suite():
	return unittest.TestLoader().loadTestsFromTestCase(bbbDAQTestCase)

"""
if __name__ == '__main__':
	allTests=unittest.TestSuite()
	allTests.addTests(bm35_suite())
	#allTests.addTests(CountsPettioner_suite())
	allTests.addTests(Reader_suite())
	allTests.addTests(SensorsManager_suite())
	allTests.addTests(DBUpdater_suite())
	#allTests.addTests(bbbDAQ_suite())
	
	unittest.TextTestRunner(verbosity=2).run(allTests)
#################################################################################################
################################Coverage_END#####################################################
cov.stop()
cov.html_report(directory='covhtml',omit=['*test*','/usr/*'])
