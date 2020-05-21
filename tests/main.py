#!/usr/bin/env python3

"""
Wrapper to run all the tests
"""

import unittest
import helper_tests
import filename_database_tests
import integration_tests
import config_tests

loader = unittest.TestLoader()
suite  = unittest.TestSuite()

suite.addTests(loader.loadTestsFromModule(helper_tests))
suite.addTests(loader.loadTestsFromModule(filename_database_tests))
suite.addTests(loader.loadTestsFromModule(integration_tests))
suite.addTests(loader.loadTestsFromModule(config_tests))

runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
