from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import cv2
import numpy as np

class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
        self.end_headers()

        cap = cv2.VideoCapture(os.getenv('SOURCEVIDEO'))

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            ret, encimg = cv2.imencode('.jpg', frame)
            self.wfile.write(bytearray('--jpgboundary\r\n', 'utf-8'))
            self.send_header('Content-type', 'image/jpeg')
            self.send_header('Content-length', str(encimg.size))
            self.end_headers()
            self.wfile.write(encimg.tobytes())

def run():
    port = int(os.getenv('WEBSITE_PORT', 80))
    server = HTTPServer(('0.0.0.0', port), CamHandler)
    print('start')
    server.serve_forever()

run()