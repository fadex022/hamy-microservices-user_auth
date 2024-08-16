FROM python:3.12.4-alpine3.20

WORKDIR /app

RUN addgroup -S hamy && adduser -S hamy -G hamy

# RUN apk update && apk add --no-cache \
#     postgresql16 postgresql16-client postgresql16-contrib gcc python3-dev libpq-dev build-essential

# RUN mkdir -p /var/lib/postgresql/data && chown -R postgres:postgres /var/lib/postgresql

# USER postgres
# RUN initdb -D /var/lib/postgresql/data

COPY ./requirements.txt /requirements.txt

RUN pip install --no-cache-dir --upgrade -r /requirements.txt

COPY . /app

USER hamy

CMD ["fastapi", "run", "main.py", "--host", "hamy-user-auth", "--port", "8000", "--workers", "5", "--reload"]