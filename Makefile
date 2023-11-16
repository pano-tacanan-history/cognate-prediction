download:
	git clone https://github.com/concepticon/concepticon-data cldf-data/concepticon/
	git clone https://github.com/pano-tacanan-history/oliveiraprotopanoan/ cldf-data/oliveiraprotopanoan/
	git clone https://github.com/pano-tacanan-history/valenzuelazariquieypanotakana/ cldf-data/valenzuelazariquieypanotakana/
	git clone https://github.com/pano-tacanan-history/girardprototakanan/ cldf-data/girardprototakanan/

preprocessing:
	python preprocessing.py

prediction:
	python predict.py

full-prediction: download preprocessing prediction
