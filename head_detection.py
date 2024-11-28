import cv2
import numpy as np
from ultralytics import YOLO
import logging

class HeadDetector:
    def __init__(self, model_path="yolov10m.pt"):
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            logging.error(f"Error loading YOLO model: {e}")
            raise

    def resize_image(self, image):
        """
        Robust image resizing with comprehensive error handling
        """
        # Check for None or invalid input
        if image is None:
            logging.error("Received None image")
            raise ValueError("Invalid image input")

        try:
            # Ensure image is a numpy array
            if not isinstance(image, np.ndarray):
                image = np.array(image)

            # Validate image dimensions
            if len(image.shape) < 2:
                logging.error(f"Invalid image shape: {image.shape}")
                raise ValueError(f"Invalid image shape: {image.shape}")

            # Handle grayscale images by converting to 3-channel
            if len(image.shape) == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

            # Calculate aspect ratio
            h, w = image.shape[:2]
            target_width = 800
            max_height = 600
            aspect_ratio = w / h

            # Determine new dimensions
            if w > h:
                # Wide image
                new_width = target_width
                new_height = int(new_width / aspect_ratio)
            else:
                # Tall image
                new_height = max_height
                new_width = int(new_height * aspect_ratio)

            # Ensure image doesn't exceed max dimensions
            if new_height > max_height:
                new_height = max_height
                new_width = int(new_height * aspect_ratio)

            # Resize image
            resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            return resized_image
        except Exception as e:
            logging.error(f"Error resizing image: {e}")
            # Return original image if resize fails
            return image if isinstance(image, np.ndarray) else None

    def detect_heads(self, frame):
        try:
            # Validate input
            if frame is None:
                logging.warning("Received None frame")
                return 0, [], [], None

            # Ensure frame is a numpy array
            if not isinstance(frame, np.ndarray):
                try:
                    frame = np.array(frame)
                except Exception as e:
                    logging.error(f"Could not convert frame to numpy array: {e}")
                    return 0, [], [], None

            # Resize input image to a consistent size
            frame = self.resize_image(frame)

            # Additional safety check
            if frame is None:
                logging.warning("Resized frame is None")
                return 0, [], [], None

            # YOLO inference
            results = self.model.predict(source=frame, save=False, conf=0.5)

            # Extract detected objects
            detections = results[0].boxes.data
            head_count = 0
            bounding_boxes = []
            confidence_scores = []

            for detection in detections:
                x1, y1, x2, y2, conf, cls = detection.cpu().numpy()
                if int(cls) == 0:  # Check if the detected class is 'person' or 'head'
                    head_count += 1
                    bounding_boxes.append([int(x1), int(y1), int(x2), int(y2)])
                    confidence_scores.append(float(conf))

                    # Draw bounding box and label
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.putText(
                        frame,
                        f"Head: {conf:.2f}",
                        (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2,
                    )

            # Add the total head count on the frame
            cv2.putText(
                frame,
                f"Total Heads: {head_count}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
            )

            return head_count, bounding_boxes, confidence_scores, frame
        except Exception as e:
            logging.error(f"Error in head detection: {e}")
            return 0, [], [], frame  # Return the original frame in case of an error