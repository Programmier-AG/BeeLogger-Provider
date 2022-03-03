FROM python:3.10-alpine

COPY . /app

WORKDIR /app

RUN rm persistant/ -r  || :
RUN rm config.py || :
RUN mv config-docker.py config.py

# Update alpine packages.
RUN apk update

# Update or install pip, setuptools and wheel.
RUN pip install --no-cache-dir --upgrade \
  pip \
  setuptools \
  wheel

RUN set -x ; \
  addgroup -g 82 -S www-data ; \
  adduser -u 82 -D -S -G www-data www-data && exit 0 ; exit 1

RUN apk add --update \
  bash \
  tmux \
  apache2 \
  apache2-dev \
  gcc \
  g++ \
  make \
  openblas \
  musl

# Install python dependencies from requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-docker.txt

ENV PYTHONPATH=/usr/lib/python3.10/site-packages

RUN chown www-data:www-data /app/ -R

EXPOSE 8000

CMD tmux new -d -s wsgi 'mod_wsgi-express start-server app.wsgi --user www-data --group www-data' ; \
  mkdir -p /tmp/mod_wsgi-localhost:8000:0/ ; \
  touch /tmp/mod_wsgi-localhost:8000:0/error_log ; \
  tail -f /tmp/mod_wsgi-localhost:8000:0/error_log
