FROM python:3.12

WORKDIR /python-docker

# Import your app.
# Most of time, it's located in the same dir as the Dockerfile:
COPY requirements.txt ./requirements.txt
COPY ./api ./api
# Install the deps. 
# Not a python expert, but start with something like:
RUN pip install -r ./requirements.txt

# Run the app.
# Different ways to do this, this is probably the simplest:
ENV FLASK_APP=./api/main
EXPOSE 5000
CMD ["flask", "run"]
