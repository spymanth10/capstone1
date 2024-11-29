import unittest
import io
import json
import numpy as np
import cv2
from app import app

class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        # Create a test client
        self.app = app.test_client()
        self.app.testing = True

    def create_test_image(self):
        """
        Create a test image in memory
        """
        # Create a blank image
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.rectangle(test_image, (25, 25), (75, 75), (255, 255, 255), -1)
        
        # Convert to bytes
        _, buffer = cv2.imencode('.jpg', test_image)
        return io.BytesIO(buffer)

    def test_home_page(self):
        """
        Test that the home page loads successfully
        """
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_valid_image_upload(self):
        """
        Test uploading a valid image
        """
        # Create a test image
        test_image = self.create_test_image()
        
        # Create a FileStorage object
        data = {
            'image': (test_image, 'test_image.jpg'),
            'input_type': 'image'
        }
        
        # Send POST request
        response = self.app.post('/process', 
                                 content_type='multipart/form-data', 
                                 data=data)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        
        # Parse JSON response
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'success')
        self.assertIn('total_heads', response_data)

    def test_invalid_file_upload(self):
        """
        Test uploading an invalid file
        """
        # Create an empty file
        data = {
            'image': (io.BytesIO(b''), 'empty_file.txt'),
            'input_type': 'image'
        }
        
        # Send POST request
        response = self.app.post('/process', 
                                 content_type='multipart/form-data', 
                                 data=data)
        
        # Expect an error response
        self.assertIn(response.status_code, [400, 500])

    def test_no_file_upload(self):
        """
        Test uploading no file
        """
        # Send POST request with no file
        response = self.app.post('/process', 
                                 content_type='multipart/form-data', 
                                 data={'input_type': 'image'})
        
        # Expect an error response
        self.assertIn(response.status_code, [400, 500])

    def test_invalid_input_type(self):
        """
        Test with invalid input type
        """
        # Create a test image
        test_image = self.create_test_image()
        
        data = {
            'image': (test_image, 'test_image.jpg'),
            'input_type': 'invalid_type'
        }
        
        response = self.app.post('/process', 
                                 content_type='multipart/form-data', 
                                 data=data)
        
        # Expect an error response
        self.assertIn(response.status_code, [400, 500])
        
        # Parse JSON response
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'error')
        self.assertIn('Invalid input type', response_data['error'])

    def test_large_file_upload(self):
        """
        Test uploading a large file
        """
        # Create a large image (larger than 10MB)
        large_image = np.zeros((4000, 4000, 3), dtype=np.uint8)
        _, large_image_buffer = cv2.imencode('.jpg', large_image)
        
        data = {
            'image': (io.BytesIO(large_image_buffer), 'large_image.jpg'),
            'input_type': 'image'
        }
        
        response = self.app.post('/process', 
                                 content_type='multipart/form-data', 
                                 data=data)
        
        # Expect an error response (either 400 or 413)
        self.assertIn(response.status_code, [400, 413])

if __name__ == '__main__':
    unittest.main()