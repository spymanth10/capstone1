import cv2
import numpy as np
from ultralytics import YOLO

class HeadDetector:
    def __init__(self, model_path="yolov8n.pt"):
        self.model = YOLO(model_path)
    
    def resize_image(self, image, target_width=800, max_height=600):
        """
        Resize image while maintaining aspect ratio
        """
        # Calculate aspect ratio
        h, w = image.shape[:2]
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
    
    def detect_heads(self, frame):
        # Resize input image to a consistent size
        frame = self.resize_image(frame)
        
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