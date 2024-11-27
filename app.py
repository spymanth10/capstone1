from flask import Flask, render_template, request, redirect, url_for, Response, flash
import cv2
import os
from ultralytics import YOLO
import atexit

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['UPLOAD_FOLDER'] = 'static/output'
app.config['MODEL_PATH'] = 'models/yolov8n.pt'

# Load the YOLO model once at startup
model = YOLO(app.config['MODEL_PATH'])

# For webcam streaming
camera = None

# Cleanup function to release camera resources
def cleanup():
    global camera
    if camera:
        camera.release()

atexit.register(cleanup)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    global camera
    option = request.form.get('option')

    if not option:
        flash("Please select an option and upload a file if required.", "error")
        return redirect(url_for('index'))

    try:
        if option == 'image':
            if 'file' not in request.files or request.files['file'].filename == '':
                flash("No image file uploaded.", "error")
                return redirect(url_for('index'))

            image = request.files['file']
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'input_image.jpg')
            image.save(image_path)

            frame = cv2.imread(image_path)
            results = model.predict(source=frame, save=False, conf=0.5)
            detections = results[0].boxes.data

            head_count = 0  # Initialize head count

            for detection in detections:
                x1, y1, x2, y2, conf, cls = detection.cpu().numpy()
                if int(cls) == 0:  # Assuming class 0 is for heads
                    head_count += 1  # Increment head count
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.putText(frame, f"Head: {conf:.2f}", (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output_image.jpg')
            cv2.imwrite(output_path, frame)
            return redirect(url_for('results', file='output_image.jpg', head_count=head_count))

        elif option == 'webcam':
            # Check if the camera is already opened; if not, open it.
            if camera is None or not camera.isOpened():
                camera = cv2.VideoCapture(0)
                if not camera.isOpened():
                    flash("Could not open webcam.", "error")
                    return redirect(url_for('index'))

            return redirect(url_for('webcam_page'))  # Redirect to webcam page

        else:
            flash("Invalid option selected.", "error")
            return redirect(url_for('index'))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('index'))

@app.route('/webcam')
def webcam_page():
    return render_template('webcam.html')

@app.route('/webcam_feed')
def webcam_feed():
    global camera

    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)

    def generate_frames():
        while True:
            ret, frame = camera.read()
            if not ret:
                break
            
            results = model.predict(source=frame, save=False, conf=0.5)
            detections = results[0].boxes.data
            
            head_count = 0  # Initialize head count for webcam feed
            
            for detection in detections:
                x1, y1, x2, y2, conf, cls = detection.cpu().numpy()
                if int(cls) == 0:  # Assuming class 0 is for heads
                    head_count += 1  # Increment head count
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.putText(frame, f"Head: {conf:.2f}", (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Display head count on the frame
            cv2.putText(frame, f"Count: {head_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/stop_webcam', methods=['POST'])
def stop_webcam():
    global camera
    if camera:
        camera.release()
        camera = None
    flash("Webcam has been stopped.", "info")
    return redirect(url_for('index'))


@app.route('/results')
def results():
    file = request.args.get('file')
    head_count = request.args.get('head_count', default=0)  # Get head count from query params
    if not file:
        flash("No file to display.", "error")
        return redirect(url_for('index'))
    return render_template('results.html', file=file, head_count=head_count)


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)