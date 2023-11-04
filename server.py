import cfg
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

# Create a session
client = BackendApplicationClient(client_id=cfg.client_id)
oauth = OAuth2Session(client=client)

# Get token for the session
token = oauth.fetch_token(token_url='https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token',
                          client_secret=cfg.client_secret)

# All requests using this session will have an access token automatically added

# data = {
#     "bbox": [13, 45, 14, 46],
#     "datetime": "2019-12-10T00:00:00Z/2019-12-10T23:59:59Z",
#     "collections": ["sentinel-1-grd"],
#     "limit": 5,
#     "next": 5,
# }

# url = "https://sh.dataspace.copernicus.eu/api/v1/catalog/1.0.0/search"
# resp = oauth.post(url, json=data)

# print(resp.content)

evalscript = """
//VERSION=3
function setup() {
  return {
    input: ["B02", "B03", "B04"],
    mosaicking: Mosaicking.ORBIT,
    output: { id: "default", bands: 3 },
  }
}

function updateOutputMetadata(scenes, inputMetadata, outputMetadata) {
  outputMetadata.userData = { scenes: scenes.orbits }
}

function evaluatePixel(samples) {
  return [2.5 * samples[1].B04, 2.5 * samples[1].B03, 2.5 * samples[1].B02]
}
"""

request = {
    "input": {
        "bounds": {
            "bbox": [
                13.822174072265625,
                45.85080395917834,
                14.55963134765625,
                46.29191774991382,
            ]
        },
        "data": [
            {
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {
                        "from": "2022-10-01T00:00:00Z",
                        "to": "2022-10-31T00:00:00Z",
                    }
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
                "format": {"type": "image/jpeg"},
            },
            {
                "identifier": "userdata",
                "format": {"type": "application/json"},
            },
        ],
    },
    "evalscript": evalscript,
}

url = "https://sh.dataspace.copernicus.eu/api/v1/process"

response = oauth.post(url, json=request)
if response.status_code == 200:
    # The request was successful
    content = response.content  # Get the response content
    
    if content:
        with open("output_image.jpg", "wb") as file:
            file.write(content)
    
    print("Response content has been saved as 'output_image.jpg'")
else:
    print(f"Request failed with status code: {response.status_code}")