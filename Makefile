.PHONY: all recepty rozvrh omezeni clean

all: recepty rozvrh omezeni

recepty:
	python3 generuj.py recepty

rozvrh:
	python3 generuj.py rozvrh

omezeni:
	python3 generuj.py omezeni

clean:
	rm -rf vystup/recepty/*.html vystup/*.html
