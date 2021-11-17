Build and run the service with `docker-compose up --build -d --scale api=4`

To end the service. Shutdown the docker container.

In case of code updates, delete the container and run the command above to rebuild the docker container before running.

To add / remove containers serving the Openroad platform, run `docker-compose up -d --scale api=8` Change the number after `api=`


## Things to Note

- Ensure Nginx conf allows for sufficient connections to handle Simulation load
  - set `events:worker_connections M` to a big number
  - set `worker_processes auto;` Do check if docker container has access to multiple processors.
- When scaling `api` check the docker process to see if the instances are running properly
  - There is a possibility that at server boot up Connection timeout occurs due to checking / creation of indexes. **NOTE:** Need to fix EVE models once the index definitions are stable
  - After scaling monitor nginx load balancing. At times, Ngins does not recognize all the upstream servers
- Nginx connections can be monitored at http://0.0.0.0:11654/nginx_status
-


