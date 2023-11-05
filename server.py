import math
import cfg
import pybase64
import json

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs


# PRIA classes
class_names = [
    "Rohttaimed",
    "Talinisu allakülvita",
    "Liblikõieliste ja kõrreliste segu (30-80% liblikõielisi)" "Suvioder allakülvita",
    "Kõrreliste rohumaa (vähemalt 80% kõrrelisi)",
    'Põldhernes, v.a "Mehis" (100% põldhernest)',
    "talioder allakülvita",
    "taliraps allakülvita",
    "suvinisu allakülvita",
    "punane ristik (100% ristikut)"
    "kaer allakülvita"
    'põlduba, v.a "Jõgeva"'
    "muu heintaimede segu",
    "rukis, v.a sangaste rukis allakülvita"
    "punane ristik (ristikut 50-80%, teisi heintaimi 20-50%)",
    "tatar allakülvita"
    "kaer liblikõieliste allakülviga"
    "suviraps allakülvita"
    "suvioder liblikõieliste allakülviga"
    "mais",
    "harilik lutsern (lutserni 50-80%, teisi heintaimi 20-50%)"
    "talirüps allakülvita"
    "forest"
    "water"
    "built_up",
]

class_names_en = [
    "Crops",
    "Winter wheat without undersowing",
    "Mixture of legumes and grasses (30-80% legumes) - Summer barley without undersowing",
    "Grassland dominated by grasses (at least 80% grasses)",
    'Field peas, except "Mehis" (100% field peas)',
    "Winter barley without undersowing",
    "Winter rapeseed without undersowing",
    "Spring wheat without undersowing",
    "Red clover (100% clover) - Oats without undersowing",
    "Field beans, except Jõgeva",
    "Other grass mixtures",
    "Rye, except Sangaste rye without undersowing",
    "Red clover (clover 50-80%, other grasses 20-50%)",
    "Buckwheat without undersowing",
    "Oats with legumes undersown",
    "Spring rapeseed without undersowing",
    "Spring barley with legumes undersown",
    "Maize",
    "Common lucerne (lucerne 50-80%, other grasses 20-50%)",
    "Winter oilseed rape without undersowing",
    "Forest",
    "Water",
    "Built-up",
]


# True Color, cloudy pixels masked out
# https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Process/Examples/S2L2A.html#true-color-cloudy-pixels-masked-out
evalscript = """
//VERSION=3
function setup() {
  return {
    input: ["B02", "B03", "B04", "SCL"],
    output: { bands: 3 },
  }
}

function evaluatePixel(sample) {
  if ([8, 9, 10].includes(sample.SCL)) {
    return [1, 0, 0]
  } else {
    return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02]
  }
}
"""


def construct_copernicus_request(lat, lng, start_time, end_time):
    return {
        "input": {
            "bounds": {
                "properties": {"crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"},
                "bbox": calculate_square_coordinates(lat, lng, 3),
            },
            "data": [
                {
                    "type": "sentinel-2-l2a",
                    "dataFilter": {
                        "timeRange": {
                            "from": start_time,
                            "to": end_time,
                        },
                        "mosaickingOrder": "leastCC",
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


def calculate_square_coordinates(latitude, longitude, radius_km):
    # Radius of the Earth in kilometers
    earth_radius = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat_rad = math.radians(latitude)
    lon_rad = math.radians(longitude)

    # Calculate the angular distance
    angular_distance = radius_km / earth_radius

    # Calculate the latitude boundaries
    lat_min = math.degrees(lat_rad - angular_distance)
    lat_max = math.degrees(lat_rad + angular_distance)

    # Calculate the longitude boundaries based on latitude
    lon_min = math.degrees(lon_rad - angular_distance / math.cos(lat_rad))
    lon_max = math.degrees(lon_rad + angular_distance / math.cos(lat_rad))

    return [lon_min, lat_min, lon_max, lat_max]


# Define the request handler class
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        return super(SimpleHTTPRequestHandler, self).end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    # Handle POST requests
    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length).decode("utf-8")

        try:
            json_data = json.loads(post_data)
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON data"}).encode("utf-8"))
            return

        lat = json_data.get("lat", None)
        lng = json_data.get("lng", None)

        if lat is None or lng is None:
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"error": "Missing lat or lng parameter"}).encode("utf-8")
            )
            return

        lat = float(lat)
        lng = float(lng)

        self.send_response(200)  # Send 200 OK status code
        self.send_header("Content-type", "application/json")
        self.end_headers()

        apr_request = construct_copernicus_request(
            lat, lng, "2023-04-01T00:00:00Z", "2023-04-29T00:00:00Z"
        )
        may_request = construct_copernicus_request(
            lat, lng, "2023-05-01T00:00:00Z", "2023-05-29T00:00:00Z"
        )
        jun_request = construct_copernicus_request(
            lat, lng, "2023-06-01T00:00:00Z", "2023-06-29T00:00:00Z"
        )

        # Create a session
        client = BackendApplicationClient(client_id=cfg.client_id)
        oauth = OAuth2Session(client=client)

        # Get token for the session
        token = oauth.fetch_token(
            token_url="https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
            client_secret=cfg.client_secret,
        )

        apr_response = oauth.post(
            "https://sh.dataspace.copernicus.eu/api/v1/process", json=apr_request
        )
        may_response = oauth.post(
            "https://sh.dataspace.copernicus.eu/api/v1/process", json=may_request
        )
        jun_response = oauth.post(
            "https://sh.dataspace.copernicus.eu/api/v1/process", json=jun_request
        )

        if apr_response.status_code == 200:
            # The request was successful
            # content = apr_response.content
            # with open("output_image.jpg", "wb") as file:
            #     file.write(content)

            # Encode the image content as base64
            apr_base64 = pybase64.b64encode(apr_response.content).decode("utf-8")
            may_base64 = pybase64.b64encode(may_response.content).decode("utf-8")
            jun_base64 = pybase64.b64encode(jun_response.content).decode("utf-8")

            self.wfile.write(
                json.dumps(
                    {
                        "class_names_en": class_names_en,
                        "apr": apr_base64,
                        "may": may_base64,
                        "jun": jun_base64,
                    }
                ).encode("utf-8")
            )

        else:
            print(f"Request failed with status code: {response.status_code}")
            self.wfile.write(
                json.dumps(
                    {"status": "Failed", "error_code": response.status_code}
                ).encode("utf-8")
            )


# Create an HTTP server with the request handler
server_address = ("", 9500)  # Listen on all available interfaces, port 8700
httpd = ThreadingHTTPServer(server_address, SimpleHTTPRequestHandler)

# Start the server
print("Server running on port 9500...")
httpd.serve_forever()
