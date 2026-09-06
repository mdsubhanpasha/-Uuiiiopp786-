.PHONY: init install run test docker clean

init:
	cp -n .env.example .env || true
	mkdir -p data /tmp/pdfs /tmp/org_messenger

install:
	pip install -r requirements.txt

sample:
	python3 scripts/test_pdfs/generate_sample_pdfs.py

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test:
	python3 -m pytest tests/test_extractor.py tests/test_api.py tests/test_sms_sender.py -v

docker:
	docker-compose up --build -d

clean:
	rm -rf /tmp/pdfs/* /tmp/org_messenger/* .pytest_cache
