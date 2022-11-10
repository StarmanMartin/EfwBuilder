FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get --assume-yes upgrade

RUN apt --assume-yes install git nodejs npm zip gzip tar

WORKDIR /opt
RUN wget "https://go.dev/dl/go1.19.3.linux-amd64.tar.gz"
RUN rm -rf /usr/local/go
RUN tar -C /usr/local -xzf go1.19.3.linux-amd64.tar.gz



RUN mkdir "/usr/local/gopath"

ENV GOROOT="/usr/local/go"
ENV GOPATH="/usr/local/gopath"

ENV PATH="${PATH}:${GOPATH}/bin:${GOROOT}/bin"

RUN go install golang.org/dl/go1.10@latest
RUN go1.10 download
RUN go1.10 get github.com/StarmanMartin/gowebdav

WORKDIR /code

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY package.json .


EXPOSE 8000

COPY build_config/entrypoint.sh /entrypoint.sh

ENTRYPOINT ["sh", "/entrypoint.sh"]
