import re
from lingpy import Wordlist, Alignments
from lingpy.read.qlc import reduce_alignment
from lingrex.util import prep_wordlist


def clean_slash(x):
    """Cleans the slash-annotation used in EDICTOR."""
    cleaned = []
    for segment in x:
        if "/" in segment:
            after_slash = re.split("/", segment)[1]
            cleaned.append(after_slash)
        else:
            cleaned.append(segment)

    return cleaned


def read_wl(path):
    """Reads in a wordlist from a CLDF dataset."""
    wordlist = Wordlist.from_cldf(
        path,
        # columns to be loaded from CLDF set
        columns=(
            "language_id",
            "concept_name",
            "concept_concepticon_gloss",
            "concept_concepticon_id",
            "segments",
            "form",
            "cognacy",
            "alignment"
            ),
        # a list of tuples of source and target
        namespace=(
            ("language_id", "doculect"),
            ("concept_concepticon_gloss", "concept"),
            ('concept_concepticon_id', 'concepticon_id'),
            ("segments", "tokens"),
            ("cognacy", "cogid")
            )
        )

    wordlist = prep_wordlist(wordlist, min_refs=2)
    alms = Alignments(wordlist, ref="cogid", transcription="tokens")

    return alms


def reduce_cogid(path, output):
    """Reduces the alignments/tokens to the trimmed version."""
    alms = read_wl(path)

    dct = {}
    for _, msa in alms.msa["cogid"].items():
        msa_reduced = []
        for site in msa["alignment"]:
            reduced = reduce_alignment([site])[0]
            reduced = clean_slash(reduced)
            msa_reduced.append(reduced)
        for i, row in enumerate(msa_reduced):
            dct[msa["ID"][i]] = row

    alms.add_entries("tokens", dct, lambda x: " ".join([y for y in x if y != "-"]), override=True)
    alms.add_entries("alignment", dct, lambda x: " ".join([y for y in x]), override=True)

    alms.output("tsv", filename=output)


# Oliveira
reduce_cogid(
    "cldf-data/oliveiraprotopanoan/cldf/cldf-metadata.json",
    output="cldf-data/oliveiraprotopanoan"
    )

# Girard
reduce_cogid(
    "cldf-data/girardprototakanan/cldf/cldf-metadata.json",
    output="cldf-data/girardprototakanan"
    )

# Valenzuela & Zariquiey
reduce_cogid(
    "cldf-data/valenzuelazariquieypanotakana/cldf/cldf-metadata.json",
    output="cldf-data/valenzuelazariquieypanotakana"
    )
