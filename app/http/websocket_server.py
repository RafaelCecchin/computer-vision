import os
import cv2
import asyncio
import websockets
import numpy as np

def get_dominant_color(roi):
    lab_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
    
    L, a, b = cv2.split(lab_roi)
    
    mean_L = np.mean(L)
    
    if mean_L < 30:
        return (0, 0, 0) 
    
    if mean_L > 220:
        return (255, 255, 255) 

    if 100 < mean_L < 180 and np.abs(np.mean(a)) < 20 and np.abs(np.mean(b)) < 20:
        return (128, 128, 128) 
    
    if np.mean(a) > 50 and np.mean(b) < 50:
        return (0, 0, 255)
    if np.mean(a) < -50 and np.mean(b) > 50:
        return (0, 255, 0) 
    if np.mean(a) < -50 and np.mean(b) < -50:
        return (255, 0, 0)
    
    mean_bgr = np.mean(roi, axis=(0, 1))
    return tuple(int(x) for x in mean_bgr)

def color_difference(c1, c2):
    return np.linalg.norm(np.array(c1) - np.array(c2))

async def video_stream(websocket):
    cap = cv2.VideoCapture(os.getenv('SOURCEVIDEO'))

    frame_count = 0
    last_dominant_color = (0,0,0)
    has_paper_color = (0,0,255)

    color_stealth_empty = (152, 161, 147)
    color_stealth_with_paper = (175, 192, 180)
    color_tolerance = 12

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            
            x_last, y_last, w_last, h_last = 5, 5, 150, 150
            cv2.rectangle(frame, (x_last, y_last), (x_last + w_last, y_last + h_last), last_dominant_color, cv2.FILLED)
            
            x_read, y_read, w_read, h_read = 325, 225, 110, 140
            color_read = (0, 255, 0)
            thickness_read = 2
            cv2.rectangle(frame, (x_read, y_read), (x_read + w_read, y_read + h_read), color_read, thickness_read)

            x_paper, y_paper, w_paper, h_paper = 305, 5, 150, 150
            cv2.rectangle(frame, (x_paper, y_paper), (x_paper + w_paper, y_paper + h_paper), has_paper_color, cv2.FILLED)
            
            frame_count += 1
            if frame_count % 3 == 0:
                roi = frame[y_read:y_read + h_read, x_read:x_read + w_read]
                dominant_color = get_dominant_color(roi)
                last_dominant_color = dominant_color
                
                diff_empty = color_difference(dominant_color, color_stealth_empty)
                diff_with_paper = color_difference(dominant_color, color_stealth_with_paper)
                
                print(last_dominant_color)

                if diff_with_paper < color_tolerance:
                    has_paper_color = (0,255,0)
                elif diff_empty < color_tolerance:
                    has_paper_color = (0,0,255)
                
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
