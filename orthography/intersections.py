"""This module computes the intersections of conceptlists"""
import csv
from csvw.dsv import UnicodeDictReader
from collections import defaultdict
from lingpy import Wordlist


def read_cl(path):
    concepts = defaultdict()
    with UnicodeDictReader(path, delimiter='\t') as reader:
        for line in reader:
            concepts[line["CONCEPTICON_GLOSS"]] = line['CONCEPTICON_ID']

    return concepts


def read_wl(path):
    wordlist = Wordlist.from_cldf(
    path,
    # columns to be loaded from CLDF set
    columns=(
        "language_id",
        "concept_name",
        "concept_concepticon_gloss",
        "segments",
        "form",
        "alignment"
        ),
    # a list of tuples of source and target
    namespace=(
        ("language_id", "doculect"),
        ("concept_concepticon_gloss", "concept"),
        ("segments", "tokens")
        )
    )
    return wordlist


def intersec(cl1, cl2):
    intersecting = defaultdict()
    missing_from_cl1 = defaultdict()

    for idx in cl2:
        if idx in cl1:
            intersecting[idx] = cl2[idx]
        else:
            missing_from_cl1[idx] = cl2[idx]

    return intersecting, missing_from_cl1


############################################
# Read in data
PATH = '../cldf-data/concepticon/concepticondata/conceptlists/'
swadesh = read_cl(PATH + "Swadesh-1952-200.tsv")
conceptlists = {
    "oliveira": read_cl(PATH + "Oliveira-2014-517.tsv"),
    "girard": read_cl('../cldf-data/girardprototakanan/etc/proto_concepts.tsv'),
    "blum": read_cl('../cldf-data/blumpanotacana/etc/concepts.tsv'),
    "valenzuela": read_cl('../cldf-data/valenzuelazariquieypanotakana/etc/concepts.tsv')
}

predictions = Wordlist("predictions/full_predictions.tsv")
oliveira = read_wl("../cldf-data/oliveiraprotopanoan/cldf/cldf-metadata.json")
valenzuela = read_wl("../cldf-data/valenzuelazariquieypanotakana/cldf/cldf-metadata.json")
blum = read_wl("../cldf-data/blumpanotacana/cldf/cldf-metadata.json")


def extract_shared(preds, dataset, name):
    conceptlist = conceptlists[name]
    intersection, _ = intersec(conceptlist, conceptlists["girard"])

    shared_forms = defaultdict()
    for word in dataset:
        if dataset[word, "concept"] in intersection and dataset[word, "doculect"] in ["ShipiboConibo", "ShipiboKonibo", "SK"]:
            form = "".join([x for x in dataset[word, "alignment"] if x not in ["-", " ", "(", ")", "+"]])
            shared_forms[dataset[word, "concept"]] = form

    output_table = [["ID", "Concept", "Concepticon", "ProtoTakana", "ProtoPano_predicted", "Doculect", "Predicted", "Form"]]
    for word in preds:
        if preds[word, "concepticon"] in shared_forms:
            preds[word, "form"] = shared_forms[preds[word, "concepticon"]]
            output_table.append(preds[word])

    # print(output_table)
    out = "predictions/shared_" + name + ".tsv"
    with open(out, 'w', encoding="utf8", newline='') as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(output_table)


extract_shared(predictions, oliveira, "oliveira")
extract_shared(predictions, valenzuela, "valenzuela")
extract_shared(predictions, blum, "blum")

no_intersection = []
for item in predictions:
    concept = predictions[item, "concepticon"]
    if concept not in conceptlists["oliveira"] and concept not in conceptlists["blum"] and concept not in conceptlists["valenzuela"]:
        no_intersection.append(predictions[item])

with open("predictions/eval_predictions.tsv", 'w', encoding="utf8", newline='') as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerows(no_intersection)
