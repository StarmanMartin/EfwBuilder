FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /opt
RUN wget "https://go.dev/dl/go1.10.8.linux-amd64.tar.gz"
RUN rm -rf /usr/local/go
RUN tar -C /usr/local -xzf go1.10.8.linux-amd64.tar.gz

ENV PATH="${PATH}:/usr/local/go/bin"

RUN mkdir "/usr/local/gopath"

ENV GOROOT="/usr/local/go"
ENV GOPATH="/usr/local/gopath"

WORKDIR /code

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN go get github.com/StarmanMartin/gowebdav

COPY build_config/entrypoint.sh /entrypoint.sh

ENTRYPOINT ["sh", "/entrypoint.sh"]
