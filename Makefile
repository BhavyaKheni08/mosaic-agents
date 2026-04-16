.PHONY: setup update test run stop clean

setup:
	pip install -r api/requirements.txt
	cd ui && npm install

run:
	docker-compose up --build

stop:
	docker-compose down

test:
	pytest api/tests
	cd ui && npm test

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf ui/node_modules
