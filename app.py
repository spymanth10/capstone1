from flask import Flask, render_template, request, send_file, Response
import cv2
import os
import pandas as pd
from head_detection import HeadDetector
import queue
import uuid
# share windows camera feed to some http/ socket port. access that socket port from docker
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULT_FOLDER'] = 'static/results'  # Change to static folder for direct web access

# Ensure upload and result folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

# Global variables for webcam streaming
webcam_queue = queue.Queue()
is_streaming = False
webcam_results = []

# Initialize Head Detector
head_detector = HeadDetector()

def generate_frames():
    global is_streaming, webcam_results
    cap = cv2.VideoCapture(0)  # Replace by `localhost:6000/get_video``
    frame_number = 0

    while is_streaming:
        ret, frame = cap.read()
        if not ret:
            break

        frame_number += 1
        head_count, bounding_boxes, confidence_scores, annotated_frame = head_detector.detect_heads(frame)

        # Store results
        webcam_results.append({
            'frame_number': frame_number,
            'head_count': head_count,
            'bounding_boxes': str(bounding_boxes),
            'confidence_scores': str(confidence_scores)
        })

        # Encode frame for streaming
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/')
def home():
    return render_template('home.html')  #change

@app.route('/process', methods=['POST'])
def process():
    input_type = request.form.get('input_type')

    if input_type == 'image':
        # Image upload processing
        if 'image' not in request.files:
            return render_template('error.html', message="No file uploaded") #change
        
        file = request.files['image']
        if file.filename == '':
            return render_template('error.html', message="No selected file") #change
        
        # Generate unique filename
        unique_filename = str(uuid.uuid4()) + '_' + file.filename
        
        # Save uploaded image
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(input_path)

        # Read image and detect heads
        frame = cv2.imread(input_path)
        head_count, bounding_boxes, confidence_scores, annotated_frame = head_detector.detect_heads(frame)

        # Save annotated image
        output_filename = 'annotated_' + unique_filename
        output_path = os.path.join(app.config['RESULT_FOLDER'], output_filename)
        cv2.imwrite(output_path, annotated_frame)

        # Save results to CSV
        results_df = pd.DataFrame({
            'Total Heads': [head_count],
            'Bounding Boxes': [str(bounding_boxes)],
            'Confidence Scores': [str(confidence_scores)]
        })
        csv_path = os.path.join(app.config['RESULT_FOLDER'], 'output_image_results.csv')
        results_df.to_csv(csv_path, index=False)

        return render_template('image_result.html', 
                               head_count=head_count, 
                               annotated_image=output_filename)

    elif input_type == 'webcam':
        # Start webcam streaming
        global is_streaming, webcam_results
        is_streaming = True
        webcam_results = []
        return render_template('webcam_result.html')

    return render_template('error.html', message="Invalid input type")

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop_webcam')
def stop_webcam():
    global is_streaming, webcam_results
    is_streaming = False

    # Save webcam results to CSV
    if webcam_results:
        results_df = pd.DataFrame(webcam_results)
        csv_path = os.path.join(app.config['RESULT_FOLDER'], 'webcam_results.csv')
        results_df.to_csv(csv_path, index=False)

    return render_template('download.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(
        os.path.join(app.config['RESULT_FOLDER'], filename),
        as_attachment=True
    )

# if __name__ == '__main__':
#     app.run(debug=True)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    jksaddhbf
