#!/usr/bin/env python3

import unittest
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import test modules
from test_learning_engine import (
    TestVectorStore,
    TestContentProcessor,
    TestKnowledgeExtractor,
    TestQueryEngine,
    TestLearningVisualizer
)

def run_tests():
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add tests to the suite
    test_suite.addTest(unittest.makeSuite(TestVectorStore))
    test_suite.addTest(unittest.makeSuite(TestContentProcessor))
    test_suite.addTest(unittest.makeSuite(TestKnowledgeExtractor))
    test_suite.addTest(unittest.makeSuite(TestQueryEngine))
    test_suite.addTest(unittest.makeSuite(TestLearningVisualizer))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return the result
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)