

.PHONY: all
all: clean lint cov build

ifeq ($(OS),Windows_NT) 
    detected_OS := Windows
	exec_name := sperf.exe
	del_exec := rmdir /Q /S
else
    detected_OS := $(shell sh -c 'uname 2>/dev/null || echo Unknown')
	exec_name := sperf
	del_exec := rm -fr 
endif

.PHONY: clean
clean:
	$(del_exec) build
	$(del_exec) dist

.PHONY: build
build:
	pyinstaller -F ./scripts/sperf
	7z a -tzip ./dist/sperf-$(detected_OS).zip ./dist/$(exec_name) -mx0

.PHONY: cov
cov:
	pytest --cov=./pysper --cov-fail-under=70 ./tests

.PHONY: test
test:
	coverage run -m unittest discover ./tests
	coverage report

.PHONY: lint
lint:
	flake8 ./pysper ./tests
	black .

.PHONY: setup
setuppy:
	env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.9.6
	pyenv local 3.9.6
	python -m venv venv
