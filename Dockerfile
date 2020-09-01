FROM python:3.8.5-alpine3.12
WORKDIR /usr/app
COPY . ./
RUN apk add --update alpine-sdk musl-dev linux-headers
RUN python -m venv .
RUN chmod +x ./bin/activate
RUN ./bin/activate
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD uwsgi --socket 0.0.0.0:5000 --protocol=http --master --enable-threads --threads 2 --thunder-lock -w wsgi:app