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

async def save_image(encimg, frame_count):
    image_name = f'./images/{frame_count}.jpg'
    print(f'Salvando imagem {image_name}')
    with open(image_name, 'wb') as f:
        f.write(encimg.tobytes())

async def video_stream(websocket):
    cap = cv2.VideoCapture(os.getenv('SOURCEVIDEO'))

    color_red = (0, 0, 255)
    color_green = (0, 255, 0)

    frame_count = 0

    last_dominant_color = (0,0,0)

    has_paper = False
    has_paper_color = color_red
    
    color_stealth_with_paper = (182, 208, 198)
    color_tolerance = 20

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            #frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            
            frame_count = frame_count + 1

            # Last dominant color
            x_last, y_last, w_last, h_last = 5, 5, 150, 150
            cv2.rectangle(frame, (x_last, y_last), (x_last + w_last, y_last + h_last), last_dominant_color, cv2.FILLED)
            
            # Read area
            x_read, y_read, w_read, h_read = 520, 300, 110, 140
            thickness_read = 2
            cv2.rectangle(frame, (x_read, y_read), (x_read + w_read, y_read + h_read), color_green, thickness_read)

            # Has paper or not
            x_paper, y_paper, w_paper, h_paper = 500, 5, 150, 150
            cv2.rectangle(frame, (x_paper, y_paper), (x_paper + w_paper, y_paper + h_paper), has_paper_color, cv2.FILLED)
            
            # Show color green if has paper and show color red if not
            roi = frame[y_read:y_read + h_read, x_read:x_read + w_read]
            dominant_color = get_dominant_color(roi)
            last_dominant_color = dominant_color   
            
            diff_with_paper = color_difference(dominant_color, color_stealth_with_paper)
            has_paper = diff_with_paper < color_tolerance
            has_paper_color = color_green if has_paper else color_red
            
            if has_paper:
                ret, img_roi = cv2.imencode('.jpg', roi, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
                await save_image(img_roi, frame_count)
            
            ret, encimg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

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

