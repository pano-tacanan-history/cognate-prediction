# Cognate Reflex Prediction as Hypothesis Test for a Deep Genealogical Relation between the Panoan and Tacanan Language Families

## Reproducting the predictions

This repository accompanies the initial submission of the article. In order to reproduce the predictions, please run the following commands:

```CLI
pip install -r requirements.txt
make full-prediction
```

## File structure

In `cldf-data`, the datasets are stored after download. The data is processed and converted to a `lingpy::Wordlist` during the preprocessing, and stored in `data/`. During the prediction, the conversion profiles (`profiles/`) are loaded, and the full list of predictions stored in `predictions`. In the same folder, the files for the pilot data are stored - the intersections of the Proto-Tacanan conceptlist with the respective concepts of the other datasets. Those files ( `shared_valenzuela` and `shared_oliveira`) include the respective forms of Shipibo-Konibo. Two copies of those files are stored in `results/`, where they are annotated for correct/incorrect predictions.
