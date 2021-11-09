Build and run the service with `docker-compose up --build -d --scale app=4`

To end the service. Shutdown the docker container.

In case of code updates, delete the container and run the command above to rebuild the docker container before running.

To add / remove containers serving the Openroad platform, run `docker-compose up -d --scale app=8` Change the number after `app=`
