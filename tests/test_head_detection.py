import unittest
import os
import sys
import numpy as np
import cv2

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from head_detection import HeadDetector

class TestHeadDetection(unittest.TestCase):
    def setUp(self):
        self.detector = HeadDetector()
    
    def test_resize_image(self):
        # Create a test image
        test_image = np.zeros((1000, 1500, 3), dtype=np.uint8)
        
        # Test resizing
        resized_image = self.detector.resize_image(test_image)
        
        # Assert image is resized correctly
        self.assertLessEqual(resized_image.shape[0], 600)
        self.assertLessEqual(resized_image.shape[1], 800)
    
    def test_detect_heads(self):
        # Create a test image
        test_image = np.zeros((400, 600, 3), dtype=np.uint8)
        
        # Detect heads
        head_count, bounding_boxes, confidence_scores, annotated_frame = self.detector.detect_heads(test_image)
        
        # Assert return types
        self.assertIsInstance(head_count, int)
        self.assertIsInstance(bounding_boxes, list)
        self.assertIsInstance(confidence_scores, list)
        self.assertIsNotNone(annotated_frame)

    def test_model_loading(self):
        # Ensure model loads without errors
        self.assertIsNotNone(self.detector.model)

if __name__ == '__main__':
    unittest.main()