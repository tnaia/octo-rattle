PYTHON=python3
MARKDOWN=markdown -f fencedcode -f nostyle

visconde.py: visconde.lt
	$(PYTHON) visconde.py --weave --fencedwithlanguage visconde.lt
	$(PYTHON) visconde.py --weave --fencedwithlanguage visconde.lt

visconde.lt.md: visconde.py
	$(PYTHON) visconde.py --weave --fencedwithlanguage visconde.lt

visconde.html: visconde.lt.md visconde.head.html visconde.tail.html
	$(MARKDOWN) visconde.lt.md > visconde.main.html
	cat visconde.head.html visconde.main.html visconde.tail.html > visconde.html
