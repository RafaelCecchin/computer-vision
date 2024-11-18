import os
from http.server import BaseHTTPRequestHandler, HTTPServer

sourceVideo = os.getenv("SOURCEVIDEO")

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = (
            "<html> \
                <head> \
                </head> \
                <body>"
                    f"<iframe src='{sourceVideo}' width='100%' height='100%'></iframe> \
                </body> \
            </html>"
        )
        self.wfile.write(bytes(html, "utf-8"))

def run(server_class=HTTPServer, handler_class=MyServer):
    server_address = ('', 80)
    httpd = server_class(server_address, handler_class)
    print("Starting httpd...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()

