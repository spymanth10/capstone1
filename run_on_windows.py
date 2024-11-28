import cv2
from flask import Flask, Response

app = Flask(__name__)

def generate_frames():
    cap = cv2.VideoCapture(0)  # Access camera device (default camera)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield the frame in multipart/x-mixed-replace format for streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/get_video')
def video_feed():
    return Response(generate_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)  # Listen on all interfaces
