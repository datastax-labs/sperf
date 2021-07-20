

.PHONY: all
all: clean update_change lint cov build
	#do it all

ifeq ($(OS),Windows_NT) 
exec_name := sperf.exe
del_exec := rmdir /Q /S
test_dir := .\\tests
pysper_dir := .\\pysper
perf_script := .\\scripts\\sperf
sperf_zip := .\\dist\\sperf-Windows
sperf_exe := .\\dist\\sperf.exe
update_change := .\\scripts\update_change.py
else
del_exec := rm -fr 
test_dir := ./tests
pysper_dir := ./pysper
sperf_script := ./scripts/sperf
sperf_zip := ./dist/sperf-$(shell sh -c 'uname 2>/dev/null || echo Unknown')
sperf_exe := ./dist/sperf
update_change := ./scripts/update_change.py
endif

.PHONY: update_change
update_change:
	$(update_change)

.PHONY: clean
clean:
	$(del_exec) build
	$(del_exec) dist

.PHONY: build
build: update_change
	pyinstaller -F $(sperf_script)
	7z a -tzip $(sperf_zip) $(sperf_exe) -mx0

.PHONY: cov
cov:
	pytest --cov=$(pysper_dir) --cov-fail-under=70 $(tests_dir)

.PHONY: test
test:
	coverage run -m unittest discover $(tests_dir)
	coverage report

.PHONY: lint
lint:
	flake8 $(pysper_dir) $(tests_dir)
	black .

.PHONY: setup
setuppy:
	env PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.9.6
	pyenv local 3.9.6
	python -m venv venv
