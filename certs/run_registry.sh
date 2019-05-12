docker container stop registry && docker container rm -v registry

docker run -d --restart=always --name registry -v /users/yangzhou/certs:/certs -e REGISTRY_HTTP_ADDR=0.0.0.0:444 -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key -p 444:444 registry:2