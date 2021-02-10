build:
	go build -o ./bin/sperf ./...

test:
	go test ./...

lint:
	golanglint-ci run