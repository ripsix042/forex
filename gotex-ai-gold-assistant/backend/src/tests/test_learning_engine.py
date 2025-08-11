import unittest
import os
import sys
import json
import shutil
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import our services
from services.vector_store import vector_store
from services.content_processor import content_processor
from services.knowledge_extractor import knowledge_extractor
from services.query_engine import query_engine
from services.learning_visualizer import learning_visualizer

class TestVectorStore(unittest.TestCase):
    def setUp(self):
        # Create a test directory
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        os.makedirs(self.test_dir, exist_ok=True)
    
    def tearDown(self):
        # Clean up test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_add_and_search(self):
        # Test adding items to vector store and searching
        vector_store.add_item("gold price trend", {"type": "test", "source": "test"})
        vector_store.add_item("support and resistance levels", {"type": "test", "source": "test"})
        
        # Search for similar items
        results = vector_store.search("price trends in gold market")
        
        # Check that we got results
        self.assertTrue(len(results) > 0)
        
        # Check that the most relevant result is about gold price
        self.assertIn("gold", results[0]["text"].lower())
        self.assertIn("price", results[0]["text"].lower())

class TestContentProcessor(unittest.TestCase):
    def setUp(self):
        # Create a test directory and file
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create a test text file
        self.test_file = os.path.join(self.test_dir, 'test.txt')
        with open(self.test_file, 'w') as f:
            f.write("Gold prices tend to rise during economic uncertainty.")
    
    def tearDown(self):
        # Clean up test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_process_text_file(self):
        # Test processing a text file
        result = content_processor.process_file(self.test_file, "document")
        
        # Check that we got text back
        self.assertIn("text", result)
        self.assertIn("Gold prices", result["text"])
        
        # Check that we got a processed date
        self.assertIn("processed_date", result)

class TestKnowledgeExtractor(unittest.TestCase):
    def test_extract_with_rules(self):
        # Test extracting knowledge using rule-based approach
        text = "Gold prices often rise when RSI indicates oversold conditions. The MACD crossover is a bullish signal."
        metadata = {"filename": "test.txt", "content_type": "document"}
        
        result = knowledge_extractor._extract_with_rules(text, metadata)
        
        # Check that we extracted concepts
        self.assertIn("concepts", result)
        self.assertTrue(len(result["concepts"]) > 0)
        
        # Check that we extracted indicators
        self.assertIn("indicators", result)
        self.assertIn("RSI", result["indicators"])
        self.assertIn("MACD", result["indicators"])

class TestQueryEngine(unittest.TestCase):
    def test_fallback_answer(self):
        # Test getting a fallback answer
        result = query_engine._generate_fallback_answer("What is the current gold price?")
        
        # Check that we got an answer
        self.assertIn("answer", result)
        self.assertTrue(len(result["answer"]) > 0)
        
        # Check that the method is fallback
        self.assertEqual(result["method"], "fallback_knowledge_base")

class TestLearningVisualizer(unittest.TestCase):
    def setUp(self):
        # Create a test directory
        self.test_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create a test processed file
        self.processed_dir = os.path.join(self.test_dir, 'processed')
        os.makedirs(self.processed_dir, exist_ok=True)
        
        # Create a sample processed file
        sample_data = {
            "metadata": {
                "filename": "test.txt",
                "content_type": "document",
                "processed_date": "2023-06-01T12:00:00"
            },
            "extracted_knowledge": {
                "concepts": ["support level", "resistance level"],
                "patterns": ["engulfing"],
                "indicators": ["RSI", "MACD"]
            }
        }
        
        with open(os.path.join(self.processed_dir, 'test.json'), 'w') as f:
            json.dump(sample_data, f)
    
    def tearDown(self):
        # Clean up test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    @patch('services.learning_visualizer.LearningVisualizer.processed_dir', new_callable=lambda: os.path.join(os.path.dirname(__file__), 'test_data/processed'))
    def test_generate_learning_stats(self, mock_processed_dir):
        # Test generating learning stats
        stats = learning_visualizer.generate_learning_stats()
        
        # Check that we got stats
        self.assertIn("total_files_processed", stats)
        self.assertIn("concepts_by_frequency", stats)
        
        # Check that we found our test concepts
        self.assertIn("support level", stats["concepts_by_frequency"])
        self.assertIn("resistance level", stats["concepts_by_frequency"])

if __name__ == '__main__':
    unittest.main()