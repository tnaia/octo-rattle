gff.html: gff.lt
	python3 ../../visconde.py --weave --fencedwithlanguage gff.lt
	markdown -f fencedcode -f nostyle gff.lt.md > gff.lt.main.html
	cat gff.head.html gff.lt.main.html gff.tail.html > gff.html
