FROM python:3.12

RUN mkdir -p /usr/src/app

# this will allow us to cache pip dependencies
ADD requirements.txt /usr/src/app/requirements.txt

RUN python -m pip install --upgrade pip && \
    python -m pip install -r /usr/src/app/requirements.txt

COPY . /usr/src/app

WORKDIR /usr/src/app

EXPOSE 5055
ENTRYPOINT [ "bash" , "/usr/src/app/src/entrypoint.sh" ]
