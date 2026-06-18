.PHONY: all recepty rozvrh clean

all: recepty rozvrh

recepty:
	python3 generuj.py recepty

rozvrh:
	python3 generuj.py rozvrh

clean:
	rm -rf vystup/recepty/*.html vystup/*.html
