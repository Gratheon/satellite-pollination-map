## gratheon/satellite-pollination-map
Given apiary/hive coordinates X,Y, this microservice is 
fetching raw map data from european satellite sentinel-2 via copernicus API,
gets ~ 4km in radius image that is 512px in dimensions,
runs classification of resulting image,
returns base64 encoded images + classification metadata to the client (frontend)


## Configuration
Edit cfg.py to set tokens

To use CASSINI API data tokens, you need to:
- [login/register into copernicus](https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/auth?client_id=cdse-public&response_type=code&scope=openid&redirect_uri=https%3A//dataspace.copernicus.eu/account/confirmed/1)
- [go to hub dashboard](https://shapps.dataspace.copernicus.eu/dashboard/#/)
- [generate oauth token](https://shapps.dataspace.copernicus.eu/dashboard/#/account/settings)
- Use tokens in code (cfg.py) as described in [API](https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Overview/Authentication.html#python)
- Make [API first requests](https://documentation.dataspace.copernicus.eu/notebook-samples/sentinelhub/introduction_to_SH_APIs.html), [Sentinel-2 in particular](https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Process/Examples/S2L2A.html)


## URLs
- Dev: http://localhost:9500
- Prod: http://satellite.gratheon.com


## Architecture

```mermaid
flowchart LR
	web-app("<a href='https://github.com/Gratheon/web-app'>web-app</a>\n:8080") --"POST / (to analyze Crop Map)"--> satellite-pollination-map
	satellite-pollination-map -- download image at coords X,Y--> sentinel
	satellite-pollination-map -- run inference --> ML[model with random forest]
```

## Development
You can run service natively
```
pip install -f requirements.txt
python server.py
```

Or you can run it as a docker container
```
docker-compose -f docker-compose.dev.yml up
```

### ML model 
Trained on CASSINI image dataset + markup of PRIA polygon data for fields + MAAAMET for forests
See [vegetation_classificator.ipynb](./vegetation_classificator.ipynb)


Model pickle file exceeds github 100mb limit so its stored here:
https://drive.google.com/file/d/1EIy687IN95hYMr-QOugzQ5mjP6VOS2Jk/view?usp=drive_link
