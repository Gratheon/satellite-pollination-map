cd /www/satellite-pollination-map/
COMPOSE_PROJECT_NAME=gratheon docker-compose down

rm -rf /www/satellite-pollination-map/

COMPOSE_PROJECT_NAME=gratheon docker-compose up -d --build