#!/usr/bin/env python3

import unittest
import local_file_tests

loader = unittest.TestLoader()
suite  = unittest.TestSuite()

suite.addTests(loader.loadTestsFromModule(local_file_tests))

runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
