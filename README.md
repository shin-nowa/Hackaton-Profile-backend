:: Pra rodar baixem o docker, criem uma .env com algo assim: (mudem se precisar)
```
    POSTGRES_USER=admin
    POSTGRES_PASSWORD=123456
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432
    POSTGRES_DB=db_usuarios

    SECRET_KEY = "123456"
    ALGORITHM = "HS256"
```
dps deem ```docker compose up -d```
dps rodem o create_database.py,
dps deem ```uvicorn main:app --reload``` pra rodar a api.