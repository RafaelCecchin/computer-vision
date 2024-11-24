import os
import cv2
import asyncio
import websockets

async def video_stream(websocket):
    cap = cv2.VideoCapture(os.getenv('SOURCEVIDEO'))
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            ret, encimg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 1])

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
