"""This module computes the intersections of conceptlists"""
import csv
from csvw.dsv import UnicodeDictReader
from collections import defaultdict
from lingpy import Wordlist

def read_cl(PATH):
    concepts = defaultdict()
    with UnicodeDictReader(PATH, delimiter='\t') as reader:
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
oliveira = read_cl(PATH + "Oliveira-2014-517.tsv")
girard = read_cl('../cldf-data/girardprototakanan/etc/proto_concepts.tsv')
blumpano = read_cl('../cldf-data/blumpanotacana/etc/concepts.tsv')

sec_opp_gpt, missing = intersec(oliveira, girard)
predictions = Wordlist("predictions/predictions.tsv")
oliveira = read_wl("../cldf-data/oliveiraprotopanoan/cldf/cldf-metadata.json")
valenzuela = read_wl("../cldf-data/valenzuelazariquieypanotakana/cldf/cldf-metadata.json")
blum = read_wl("../cldf-data/blumpanotacana/cldf/cldf-metadata.json")


def extract_shared(preds, dataset, name):
    shared_forms = defaultdict()
    for item in dataset:
        if dataset[item, "concept"] in sec_opp_gpt and dataset[item, "doculect"] in ["ShipiboConibo", "ShipiboKonibo", "SK"]:
            form = "".join([x for x in dataset[item, "alignment"] if x not in ["-", " ", "(", ")", "+"]])
            shared_forms[dataset[item, "concept"]] = form

    output_table = [["ID", "Concept", "Concepticon", "ProtoTakana", "ProtoPano_predicted", "Doculect", "Predicted", "Form"]]
    for item in preds:
        if preds[item, "concepticon"] in shared_forms:
            preds[item, "form"] = shared_forms[preds[item, "concepticon"]]
            output_table.append(preds[item])

    # print(output_table)
    out = "predictions/shared_" + name + ".tsv"
    with open(out, 'w', encoding="utf8", newline='') as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(output_table)


extract_shared(predictions, oliveira, "oliveira")
extract_shared(predictions, valenzuela, "valenzuelazariquiey")
extract_shared(predictions, blum, "blum")
