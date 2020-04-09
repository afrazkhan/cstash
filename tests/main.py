#!/usr/bin/env python3

import unittest
import local_file_tests
import filename_database_tests
import integration_tests

loader = unittest.TestLoader()
suite  = unittest.TestSuite()

suite.addTests(loader.loadTestsFromModule(local_file_tests))
suite.addTests(loader.loadTestsFromModule(filename_database_tests))
suite.addTests(loader.loadTestsFromModule(integration_tests))

runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
