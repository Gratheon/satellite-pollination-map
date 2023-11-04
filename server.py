import cfg
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import json
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
    # Handle POST requests
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        post_params = parse_qs(post_data)

        lat = post_params.get('lat', [None])[0]
        lng = post_params.get('lng', [None])[0]

        if(lat is None): 
            self.send_response(400);
            return
        
        if(lng is None):
            self.send_response(400);
            return

        lat = float(lat)
    
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

            print("Response content has been saved as 'output_image.jpg'")
        else:
            print(f"Request failed with status code: {response.status_code}")

        self.wfile.write(json.dumps({
            'status': 'Downloaded'
            }).encode('utf-8'))


# Create an HTTP server with the request handler
server_address = ('', 9500)  # Listen on all available interfaces, port 8700
httpd = ThreadingHTTPServer(server_address, SimpleHTTPRequestHandler)

# Start the server
print('Server running on port 9500...')
httpd.serve_forever()
