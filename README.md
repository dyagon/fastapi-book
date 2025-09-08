# fastapi-book

## dev setup

```bash
uv venv
uv sync
```

### docker

- postgres:15-alpine: 25432
- redis:7-alpine: 26379
- rabbitmq:management-alpine: 25672, 25673

```bash
docker-compose -p fastapi -f docker/docker-compose.yaml up -d 
```

### db migration

```bash
# alembic revision --autogenerate -m "Initial migration" 
uv run alembic upgrade head
```


### init db data

```bash
docker-compose -p fastapi -f docker/docker-compose.yaml exec postgres psql -U admin -d fastapi_book -f /init-data/init_hospital.sql
```



