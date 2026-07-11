# Cleanup policy

`docker system df` is a survey, not authorization. Prefer `docker image prune`, `docker container prune`, `docker volume prune`, and `docker builder prune` as separate reviewed operations. Volumes may contain the only copy of application data. `docker system prune -a --volumes` is a compound destructive action and must enumerate its widened scope before approval.

An export of a container filesystem does not preserve volume data, image history, environment secrecy, or orchestration configuration. Record `docker inspect` data carefully because it may contain credentials.
