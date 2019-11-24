.PHONY: follow-compose follow-service

follow-compose:
	watch -n 1 cat docker-compose.yml

follow-service:
	watch -n 1 cat .current_service
