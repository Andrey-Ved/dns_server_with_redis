## DNS server with Redis

Simple DNS server with Redis backend

(Python, [DNSlib](https://github.com/paulc/dnslib), [Dynaconf](https://www.dynaconf.com/), [Redis](https://redis.io/docs/))

Based on [dnserver by Samuel Colvin](https://github.com/samuelcolvin/dnserver)
  
  
### Launching in Docker

Create and start container:
```bash
$ docker-compose up
```
Stop lifted containers:
```bash
$ docker-compose stop
```
Start stopped containers:
```bash
$ docker-compose start
```
Stop and delete containers and network:
```bash
$ docker-compose down
```
Remove app image:
```bash
$ docker rmi dns_server
```
Clear logs:
```bash
$ sudo rm -rf logs/*
```