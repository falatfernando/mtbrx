# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-09-21

### Added
- **Multimodal search**: the search bar accepts a locus tag (`Rv0677c`), a gene
  symbol (`mmpS5`) or a full variant (`katG_Ser315Thr`), normalises input, and
  up-converts legacy one-letter notation (`katG_S315T`) to the three-letter
  form used by the WHO catalogue.
- **Enter to search**: the input is wrapped in a form, so pressing `Enter`
  submits the query without reloading the page.
- **Mutation-only guard**: a mutation typed without its gene (`Ser315Thr`) is
  blocked with an advisory explaining the required `gene_mutation` format.
- **Variant deep linking**: searching a full variant loads the gene and
  automatically selects, highlights and pages to that mutation in both the
  Drug Resistance Profile and the Genomic Coordinates tables.
- **Reactive selection**: the resistance table, coordinates table and
  Coordinate Analysis card share one selection, linked in both directions.
- **Gene Neighbourhood track**: an interactive, prokaryote-native track where
  clicking any gene loads it into the whole dashboard, and hovering shows gene
  symbol, locus tag, product, functional note and coordinates.
- **Sequence Retrieval panel**: coding sequence, protein translation
  (bacterial codon table 11) and adjustable upstream/downstream flanks
  (default ±500 bp), with copy-to-clipboard.
- **Non-catalogue notice**: genes annotated in H37Rv but absent from the WHO
  catalogue now show an explicit status card instead of an empty table prompt.
- **Protein length**: the gene overview reports length as `2,223 bp (740 aa)`.
- **Full WHO schema**: the resistance table gained `Effect`, `Comment`,
  `CHANGES vs ver1`, `Relaxed thresholds simulation` and `Silent mutation`,
  with a column-visibility control and emphasis on remarks and version changes.
- **Browse by Drug**: a catalogue browser grouping genes by drug, first-line
  drugs first, with per-gene mutation counts; clicking a gene loads it.
- **Catalogue Summary**: per-gene and per-drug summary tables with tier,
  confidence-grading and loss-of-function counts, plus aggregate totals.
- **Branding and citation**: enlarged, linked LaPAM logo, USP institutional
  mark, formal attribution, licence and DOI badges, and a "How to Cite" modal
  with copyable citation text and BibTeX.
- Tests for query parsing, the data layer and the table builders.

### Changed
- **Prokaryotic genome browser**: the annotation served to JBrowse is
  flattened to one gene-level feature per locus. *M. tuberculosis* has no
  splicing, so the redundant gene/CDS hierarchy and every intron control are
  removed at the source rather than hidden.
- **Genomic Coordinates table**: scrolls horizontally, shortens long indel
  alleles to a fixed width with the full sequence on hover, keeps cell text
  selectable, and offers clipboard copy for multi-kilobase alleles.
- Gene lookup is served from an in-memory annotation index instead of a
  per-query SQLite scan, and catalogue gene aliases are derived from the
  annotation rather than a hand-maintained list, so all 65 catalogue genes
  resolve from either identifier.

### Fixed
- `coordinate_calculator` referenced `DataLoader`, `GeneInfo` and `typing`
  names it never imported, which raised `NameError` on Python below 3.14.
- The coordinate derivation text used nested same-quote f-strings, a syntax
  error before Python 3.12.
- Commas in GFF3 attribute values are escaped, so a product such as
  "KatG,catalase-peroxidase" is no longer parsed as two values.

## [1.0.0] - 2026-06-29

### Added
- **Gene Search**: Interactive lookup for *Mycobacterium tuberculosis* genes with full annotation display (locus tag, coordinates, product).
- **JBrowse Integration**: Built-in genomic browser leveraging `dash-jbrowse` to visualize gene models, genomic tracks, and custom sequence alignments.
- **Coordinate Calculator**: Utility for translating between gene-relative (HGVS c. and p. notation) and absolute genomic coordinates.
- **WHO Catalogue Integration**: Preloaded WHO tuberculosis mutation catalogue for drug resistance annotations.
- **Packaging and CI Setup**: Included standard `setup.py` packaging, unit tests, and GitHub Actions CI workflow.
