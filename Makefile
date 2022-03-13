all : run

gen_net_config:
	python3 gen_net_config.py archi.yml

gen_docker-compose :
	python3 gen_docker-compose.py archi.yml

build : gen_docker-compose gen_net_config
	sudo docker-compose build

run : build
	sudo docker-compose up --detach --remove-orphans

sh :
	sudo docker exec -ti server0 sh

validated :
	sudo docker exec -ti server0 cat validated.txt

result :
	sudo docker exec -ti server0 cat result.txt

attach : build
	sudo docker-compose up --remove-orphans

kill :
	sudo docker kill $$(docker ps -a -q)

prune :
	sudo docker system prune -a

clean :
	rm docker-compose.yml
	rm server/encoins-config/net_config.yml
	rm client/net_config.yml