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
    input: [
      {
        bands: ["B04", "B08"],
      },
    ],
    output: {
      id: "default",
      bands: 3,
    },
  }
}

function evaluatePixel(sample) {
  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04)

  if (ndvi < -0.5) return [0.05, 0.05, 0.05]
  else if (ndvi < -0.2) return [0.75, 0.75, 0.75]
  else if (ndvi < -0.1) return [0.86, 0.86, 0.86]
  else if (ndvi < 0) return [0.92, 0.92, 0.92]
  else if (ndvi < 0.025) return [1, 0.98, 0.8]
  else if (ndvi < 0.05) return [0.93, 0.91, 0.71]
  else if (ndvi < 0.075) return [0.87, 0.85, 0.61]
  else if (ndvi < 0.1) return [0.8, 0.78, 0.51]
  else if (ndvi < 0.125) return [0.74, 0.72, 0.42]
  else if (ndvi < 0.15) return [0.69, 0.76, 0.38]
  else if (ndvi < 0.175) return [0.64, 0.8, 0.35]
  else if (ndvi < 0.2) return [0.57, 0.75, 0.32]
  else if (ndvi < 0.25) return [0.5, 0.7, 0.28]
  else if (ndvi < 0.3) return [0.44, 0.64, 0.25]
  else if (ndvi < 0.35) return [0.38, 0.59, 0.21]
  else if (ndvi < 0.4) return [0.31, 0.54, 0.18]
  else if (ndvi < 0.45) return [0.25, 0.49, 0.14]
  else if (ndvi < 0.5) return [0.19, 0.43, 0.11]
  else if (ndvi < 0.55) return [0.13, 0.38, 0.07]
  else if (ndvi < 0.6) return [0.06, 0.33, 0.04]
  else return [0, 0.27, 0]
}
"""

request = {
    "input": {
        "bounds": {
            "properties": {"crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            -94.04798984527588,
                            41.7930725281021,
                        ],
                        [
                            -94.04803276062012,
                            41.805773608962866,
                        ],
                        [
                            -94.06738758087158,
                            41.805901566741305,
                        ],
                        [
                            -94.06734466552734,
                            41.7967199475024,
                        ],
                        [
                            -94.06223773956299,
                            41.79144072064381,
                        ],
                        [
                            -94.0504789352417,
                            41.791376727347966,
                        ],
                        [
                            -94.05039310455322,
                            41.7930725281021,
                        ],
                        [
                            -94.04798984527588,
                            41.7930725281021,
                        ],
                    ]
                ],
            },
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
                "format": {
                    "type": "image/jpeg",
                    "quality": 80,
                },
            }
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