import os
import sys

# Ensure parent directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

from search_utils import (
    MUTATION_ADVICE,
    looks_like_locus_tag,
    looks_like_mutation,
    normalize_mutation,
    normalize_query,
    parse_query,
    strip_mutation_prefix,
)

# Gene symbols and locus tags the parser is expected to recognise (TASK-02).
KNOWN_GENES = {
    "katg", "rv1908c", "mmps5", "rv0677c", "rv0678", "whib7", "ppe35", "rrs", "dnaa",
}


def resolver(token):
    return token.lower() in KNOWN_GENES


@pytest.mark.parametrize("raw,expected", [
    ("  katG  ", "katG"),
    ("_katG_", "katG"),
    ("katG_Ser315Thr ", "katG_Ser315Thr"),
    ("kat G", "katG"),
    ("", ""),
    (None, ""),
])
def test_normalize_query_strips_whitespace_and_separators(raw, expected):
    assert normalize_query(raw) == expected


@pytest.mark.parametrize("raw,expected", [
    # Three-letter notation is the WHO catalogue standard.
    ("Ser315Thr", "p.Ser315Thr"),
    ("p.Ser315Thr", "p.Ser315Thr"),
    ("p.ser315thr", "p.Ser315Thr"),
    # Legacy one-letter input is up-converted.
    ("S315T", "p.Ser315Thr"),
    ("D47G", "p.Asp47Gly"),
    # Consequence suffixes are preserved.
    ("Asp47fs", "p.Asp47fs"),
    ("Met1?", "p.Met1?"),
    ("LoF", "LoF"),
    # Nucleotide notation passes through, normalised.
    ("c.1349C>T", "c.1349C>T"),
    ("c.-15c>t", "c.-15C>T"),
])
def test_normalize_mutation(raw, expected):
    assert normalize_mutation(raw) == expected


@pytest.mark.parametrize("token", ["Rv0001", "Rv0677c", "Rv1963A", "Rvnr01", "Rvnt02"])
def test_locus_tags_are_recognised(token):
    assert looks_like_locus_tag(token)


@pytest.mark.parametrize("token", ["katG", "mmpS5", "Ser315Thr", "PPE35", "Rv12345"])
def test_non_locus_tags_are_rejected(token):
    assert not looks_like_locus_tag(token)


@pytest.mark.parametrize("token", ["Ser315Thr", "p.Ser315Thr", "S315T", "Asp47fs", "c.-15C>T"])
def test_standalone_mutations_are_detected(token):
    assert looks_like_mutation(token)


@pytest.mark.parametrize("token", ["zzz999", "abc123", "katG", "Rv0678"])
def test_arbitrary_identifiers_are_not_mutations(token):
    """An unknown identifier is a missing gene, not a malformed mutation."""
    assert not looks_like_mutation(token)


@pytest.mark.parametrize("raw,gene,mutation", [
    ("katG_Ser315Thr", "katG", "p.Ser315Thr"),
    ("katG_p.Ser315Thr", "katG", "p.Ser315Thr"),
    ("katG_S315T", "katG", "p.Ser315Thr"),
    ("Rv0678_Asp47fs", "Rv0678", "p.Asp47fs"),
    ("katG_c.1349C>T", "katG", "c.1349C>T"),
])
def test_variant_queries_split_gene_and_mutation(raw, gene, mutation):
    """TASK-04: a full variant resolves to both a gene and a mutation."""
    parsed = parse_query(raw, gene_resolver=resolver)
    assert parsed.kind == "variant"
    assert parsed.gene_token == gene
    assert parsed.mutation == mutation
    assert parsed.variant == f"{gene}_{mutation}"


@pytest.mark.parametrize("raw", ["katG", "Rv0677c", "mmpS5", "whiB7", "PPE35", "rrs"])
def test_gene_queries(raw):
    """TASK-02: locus tags and gene symbols are both accepted."""
    parsed = parse_query(raw, gene_resolver=resolver)
    assert parsed.kind == "gene"
    assert parsed.gene_token == raw


@pytest.mark.parametrize("raw", ["Ser315Thr", "p.Ser315Thr", "S315T", "Asp47fs"])
def test_mutation_without_gene_is_flagged(raw):
    """TASK-03: a bare mutation is blocked with an advisory message."""
    parsed = parse_query(raw, gene_resolver=resolver)
    assert parsed.kind == "standalone_mutation"
    assert parsed.gene_token is None
    assert parsed.message == MUTATION_ADVICE


def test_empty_query():
    assert parse_query("   ", gene_resolver=resolver).kind == "empty"


def test_unknown_identifier_is_treated_as_a_gene_lookup():
    """So the user sees "gene not found" rather than mutation formatting advice."""
    assert parse_query("zzz999", gene_resolver=resolver).kind == "gene"


@pytest.mark.parametrize("raw,expected", [
    ("p.Ser315Thr", "Ser315Thr"),
    ("c.1349C>T", "1349C>T"),
    ("Ser315Thr", "Ser315Thr"),
    (None, ""),
])
def test_strip_mutation_prefix(raw, expected):
    assert strip_mutation_prefix(raw) == expected
