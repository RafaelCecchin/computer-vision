import os
from flask import Flask, render_template

base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, "../views")

app = Flask(__name__, template_folder=template_dir)

@app.route('/')
def index():
    return render_template('index.html', ws_port=os.getenv('WEBSOCKET_PORT', 8765))

if __name__ == '__main__':
    port = int(os.getenv('WEBSITE_PORT', 80))
    app.run(host='0.0.0.0', port=port)
