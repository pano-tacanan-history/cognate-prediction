from collections import defaultdict
from csvw.dsv import UnicodeDictReader
import requests


url = 'https://osf.io/download/wd6se/'
r = requests.get(url, timeout=10)

with open('predictions/predictions_prereg.tsv', 'wb') as f:
    f.write(r.content)


def read_cl(path):
    """Reads in a conceptlist from a file."""
    predictions = defaultdict()
    with UnicodeDictReader(path, delimiter='\t') as reader:
        for line in reader:
            predictions[line['ID']] = line['Predicted']

    return predictions


original = read_cl('predictions/predictions_prereg.tsv')
new = read_cl('predictions/core_predictions.tsv')

changes = []
for item in original:
    if original[item] != new[item]:
        changes.append(original[item])

if len(changes) == 0:
    print('All good, the predictions are the same as in the pre-registered version.')
else:
    print(f'The following {len(changes)} forms have changed their prediction:')
    for item in changes:
        print(item, original[item])
