download:
	git clone https://github.com/concepticon/concepticon-data --branch v3.1.0 cldf-data/concepticon/
	git clone https://github.com/pano-tacanan-history/oliveiraprotopanoan/ --branch v1.1.2 cldf-data/oliveiraprotopanoan/
	git clone https://github.com/pano-tacanan-history/valenzuelazariquieypanotakana/ --branch v1.0.0 cldf-data/valenzuelazariquieypanotakana/
	git clone https://github.com/pano-tacanan-history/girardprototakanan/ --branch v1.0.0 cldf-data/girardprototakanan/

preprocessing:
	python preprocessing.py

prediction:
	python predict.py

full-prediction: download preprocessing prediction
