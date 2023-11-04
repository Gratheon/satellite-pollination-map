import cfg
import pybase64
import json

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

# Create a session
client = BackendApplicationClient(client_id=cfg.client_id)
oauth = OAuth2Session(client=client)

start_time = "2023-04-15T00:00:00Z"
end_time = "2023-07-15T00:00:00Z"

# Get token for the session
token = oauth.fetch_token(
    token_url="https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
    client_secret=cfg.client_secret,
)
evalscript = """
//VERSION=3
function setup() {
  return {
    input: ["B02", "B03", "B04"],
    output: { bands: 3 },
  }
}

function evaluatePixel(sample) {
  return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02]
}
"""

copernicus_request = {
    "input": {
        "bounds": {
            "properties": {"crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"},
            "bbox": [
                13.822174072265625,
                45.85080395917834,
                14.55963134765625,
                46.29191774991382,
            ],
        },
        "data": [
            {
                "type": "sentinel-2-l1c",
                "dataFilter": {
                    "timeRange": {
                        "from": start_time,
                        "to": end_time,
                    },
                    "mosaickingOrder": "leastRecent",
                },
            }
        ],
    },
    "output": {
        "width": 512,
        "height": 512,
        "responses": [
            {
                "identifier": "default",
                "format": {"type": "image/png"},
            }
        ],
    },
    "evalscript": evalscript,
}

# Define the request handler class
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        return super(SimpleHTTPRequestHandler, self).end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    # Handle POST requests
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')

        try:
            json_data = json.loads(post_data)
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid JSON data'}).encode('utf-8'))
            return

        lat = json_data.get('lat', None)
        lng = json_data.get('lng', None)

        if lat is None or lng is None:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Missing lat or lng parameter'}).encode('utf-8'))
            return

        lat = float(lat)
        lng = float(lng)

        copernicus_request["input"]["bounds"]["bbox"] = [
            lat-0.1,
            lng-0.1,
            lat+0.1,
            lng+0.1,
        ]
        
        self.send_response(200)  # Send 200 OK status code
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response = oauth.post("https://sh.dataspace.copernicus.eu/api/v1/process", json=copernicus_request)

        if response.status_code == 200:
            # The request was successful
            content = response.content  # Get the response content
            if content:
                with open("output_image.jpg", "wb") as file:
                    file.write(content)
                    
                # Encode the image content as base64
                image_base64 = pybase64.b64encode(content).decode('utf-8')

                self.wfile.write(json.dumps({
                    'status': 'Downloaded',
                    'image_base64': image_base64
                }).encode('utf-8'))
            else:
                self.wfile.write(json.dumps({'status': 'No image available'}).encode('utf-8'))

        else:
            print(f"Request failed with status code: {response.status_code}")
            self.wfile.write(json.dumps({
                'status': 'Failed',
                'error_code': response.status_code
            }).encode('utf-8'))

# Create an HTTP server with the request handler
server_address = ('', 9500)  # Listen on all available interfaces, port 8700
httpd = ThreadingHTTPServer(server_address, SimpleHTTPRequestHandler)

# Start the server
print('Server running on port 9500...')
httpd.serve_forever()
