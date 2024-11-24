import os
import cv2
import asyncio
import websockets

base_dir = os.path.dirname(os.path.abspath(__file__))

async def video_stream(websocket):
    cap = cv2.VideoCapture(os.getenv('SOURCEVIDEO'))
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    monica = cv2.imread(os.path.join(base_dir, "../assets/monica.png"))

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            frame = cv2.resize(frame, (0,0), fx=0.5, fy=0.5)
            
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(frame_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            for (x, y, w, h) in faces:
                monica_scaled = cv2.resize(monica, (w, h))
                frame[y:y+h, x:x+w] = monica_scaled

            ret, encimg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])

            try:
                await websocket.send(encimg.tobytes())
            except websockets.exceptions.ConnectionClosedError:
                print("Connection closed by client")
                break
    finally:
        cap.release()

async def main():
    port = int(os.getenv('WEBSOCKET_PORT', 8765))
    async with websockets.serve(video_stream, "0.0.0.0", port):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

