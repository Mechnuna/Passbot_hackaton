run_app:
	python3 src/xmain.py

run_web:
	python3 src/webapp/app.py

run_bot:
	python3 src/main.py

run_test:
	cd src; python -m unittest discover tests
