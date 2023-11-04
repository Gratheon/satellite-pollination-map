## gratheon/satellite-pollination-map
Given apiary/hive coordinates X,Y,time
this microservice is fetching raw map data from Copernicus,
then runs segmentation and classification

https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Overview/Authentication.html#python


### URLs
- Dev: http://localhost:9500


## Architecture

```mermaid
flowchart LR
    web-app("<a href='https://github.com/Gratheon/web-app'>web-app</a>\n:8080") --analyzeCropMap--> satellite-pollination-map

	satellite-pollination-map -- download image at coords X,Y--> sentinel
	satellite-pollination-map -- run inference --> ML[model with random forest]
```

### ML model 
Trained on CASSINI image dataset + markup of PRIA polygon data for fields + MAAAMET for forests
See [vegetation_classificator.ipynb](./vegetation_classificator.ipynb)