FROM golang:1.17.2-alpine3.14
WORKDIR /go/src
COPY go.mod go.sum ./
RUN go mod download
COPY server.go .
ENTRYPOINT ["go", "run", "server.go"]
