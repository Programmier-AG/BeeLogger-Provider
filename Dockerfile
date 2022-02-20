FROM python:3.10-alpine

COPY . /app

WORKDIR /app

# Update alpine packages.
RUN apk update

# Update or install pip, setuptools and wheel.
RUN pip install --no-cache-dir --upgrade \
  pip \
  setuptools \
  wheel

# Install python dependencies from requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt

# Run the python script.
CMD [ "python3", "./app.py"]