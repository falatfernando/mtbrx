# AI Agent Implementation Spec: TBDashboard Enhancements & Bug Fixes

## System Context & Overview
**Repository / Application:** TBDashboard (Web dashboard for *Mycobacterium tuberculosis* WHO drug resistance catalogue visualization and genome browser).  
**Domain Constraints:**
- Organism: *Mycobacterium tuberculosis* (prokaryote / bacterium).
- Splicing / Introns do NOT exist in this biology. A bacterial coding sequence (CDS) is equivalent to the gene for functional bioinformatics purposes.
- Catalogue Reference: WHO catalogue of mutations in *Mycobacterium tuberculosis* complex and their association with drug resistance.
- Variant standard notation: Three-letter amino acid code prefixed by gene and underscore (e.g., `katG_Ser315Thr`), not one-letter abbreviation (e.g., avoid `katG_S315T`).

---

## Agent Execution Checklist & Task Registry

| Task ID | Component / Area | Priority | Status |
| :--- | :--- | :--- | :--- |
| `TASK-01` | Search Form: Enter Key Trigger | P0 (Critical) | Done |
| `TASK-02` | Search Form: Notation & Multimodal Input | P1 (High) | Done |
| `TASK-03` | Search Form: Mutation-Only Validation Guard | P1 (High) | Done |
| `TASK-04` | Search Form: Direct Variant Query Resolution | P1 (High) | Done |
| `TASK-05` | Search Feedback: Non-Catalogue Gene Banner | P1 (High) | Done |
| `TASK-06` | Main Card: Nucleotide & Protein (aa) Length | P1 (High) | Done |
| `TASK-07` | Genomic Table: Horizontal Overflow & Text Selection | P0 (Critical) | Done |
| `TASK-08` | Table Sync: Drug Resistance Selection Reactive Linking | P1 (High) | Done |
| `TASK-09` | Genome Browser: Prokaryotic De-eukaryotization | P1 (High) | Done — fixed at the data level, see note |
| `TASK-10` | Genome Browser: Neighbor Gene Interactive Navigation | P1 (High) | Done — via a new Plotly track, see note |
| `TASK-11` | Genome Browser: Enriched Hover Tooltip | P2 (Medium) | Done — via a new Plotly track, see note |
| `TASK-12` | Resistance Table: Additional WHO Metadata Columns | P1 (High) | Done |
| `TASK-13` | New Feature: Browse by Drug Module | P2 (Medium) | Done |
| `TASK-14` | New Feature: Catalogue Summary Statistics View | P2 (Medium) | Done |
| `TASK-15` | Branding & Footer: USP, LaPAM, GitHub & Citations | P2 (Medium) | Done — lab GitHub org and usp.png pending |

---

## Detailed Task Specifications

### `TASK-01`: Search Form `Enter` Key Event Handler
- **Target File(s):** Search bar component (e.g., `src/components/Search/SearchBar.tsx` or similar).
- **Issue:** Search currently executes only when clicking the magnifying glass icon; pressing `Enter` has no effect.
- **Requirements:**
  1. Wrap the search input within a `<form>` element if not already present.
  2. Implement an `onKeyDown` or form `onSubmit` handler:
     ```typescript
     const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
       if (e.key === 'Enter') {
         e.preventDefault();
         handleSearchSubmit();
       }
     };
     ```
  3. Ensure `onSubmit` invokes `event.preventDefault()` to prevent unwanted browser navigation.
- **Verification:**
  - Type `katG` in the search bar and press `Enter`. The query must execute immediately without clicking the search button.

---

### `TASK-02`: Search Bar Notation & Multimodal Input
- **Target File(s):** Search input component and query parser utility.
- **Issue:** Placeholder displays `katG_S315T` (single-letter code). The system must standardize on three-letter amino acid nomenclature and accept three search formats.
- **Requirements:**
  1. Update input placeholder to:
     `"Search gene ID (e.g., Rv0677c), gene name (e.g., mmpS5), or variant (e.g., katG_Ser315Thr)..."`
  2. Update quick-access pills or helper text to state support for:
     - Locus Tag / Gene ID (e.g., `Rv0677c`)
     - Gene Name / Symbol (e.g., `mmpS5`)
     - Variant Name (e.g., `katG_Ser315Thr`)
  3. Normalize inputs on submission (strip whitespace, trim leading/trailing separators).
- **Verification:**
  - Check placeholder string rendering.
  - Search by locus tag `Rv0677c` $\rightarrow$ loads `mmpS5`.
  - Search by gene name `katG` $\rightarrow$ loads `katG` (`Rv1907c`).

---

### `TASK-03`: Mutation-Only Query Detection & Advisory Alert
- **Target File(s):** Search validation handler, Toast / Alert banner component.
- **Issue:** When users type a raw mutation like `Ser315Thr` or `p.Ser315Thr` without a gene prefix, queries fail or return ambiguous results.
- **Requirements:**
  1. Define a regular expression matching standalone mutation patterns:
     ```typescript
     const STANDALONE_MUTATION_REGEX = /^(p\.)?([A-Z][a-z]{2}|\b[A-Z]\b)\d+([A-Z][a-z]{2}|\b[A-Z]\b|LoF|\?|\*)$/i;
     ```
  2. If the input matches this pattern (and does not contain an underscore `_` or valid locus tag):
     - Block blank/failed search execution.
     - Render an inline alert / toast:
       `"Please specify the gene name followed by an underscore and the mutation (e.g., katG_Ser315Thr). A mutation alone cannot be resolved uniquely across the genome."`
- **Verification:**
  - Type `Ser315Thr` and press enter $\rightarrow$ alert appears instructing the user to format as `katG_Ser315Thr`.

---

### `TASK-04`: Direct Variant Search Resolution & Deep Linking
- **Target File(s):** Search router, State store / Context (`VariantContext` / `useGeneStore`).
- **Issue:** Entering a complete variant (e.g., `katG_Ser315Thr`) navigates to the gene in the browser but fails to select or highlight the variant in the table.
- **Requirements:**
  1. Parse variant input by delimiter `_`:
     - Token 0: Gene symbol or locus tag (`katG`).
     - Token 1: Mutation string (`Ser315Thr`).
  2. Update active gene to `katG`.
  3. Dispatch state update for `activeMutation` or `selectedVariant = "p.Ser315Thr"` (handling optional `p.` prefix normalization).
  4. In the **Drug Resistance Profile** table:
     - Auto-paginate or scroll to the row matching the parsed mutation.
     - Apply an active highlight class (e.g., `bg-primary/20` or equivalent selection state).
  5. In the **Genomic Coordinates** table:
     - Filter or scroll to matching coordinates for this variant.
- **Verification:**
  - Search `katG_Ser315Thr`. Confirm `katG` loads, and row `p.Ser315Thr` is automatically selected and highlighted.

---

### `TASK-05`: Non-Catalogue Gene Feedback State
- **Target File(s):** Coordinate Analysis Card, Gene View Container.
- **Issue:** When querying an *M. tuberculosis* gene that exists in the reference annotation but has no entries in the WHO resistance catalogue, the UI displays an irrelevant prompt: *"Selection required: Click a row in the Genomic Coordinates table above."*
- **Requirements:**
  1. Check if the active gene is present in the WHO catalogue dataset:
     ```typescript
     const isInCatalogue = catalogueGenes.includes(currentGene.locusTag) || catalogueGenes.includes(currentGene.name);
     ```
  2. If `isInCatalogue === false`:
     - Render the genome browser track normally (reference genome remains visible).
     - In place of the variant and coordinate analysis tables, render a clear status card:
       ```html
       <div class="info-card">
         <h4>Gene Not in WHO Catalogue</h4>
         <p>
           <strong>{geneName} ({locusTag})</strong> is part of the <em>M. tuberculosis</em> reference genome (H37Rv)
           but is not currently indexed in the WHO catalogue of drug resistance-associated mutations.
         </p>
       </div>
       ```
- **Verification:**
  - Search a non-resistance housekeeping gene (e.g., `dnaA` / `Rv0001`). Verify the explicit non-catalogue notice is displayed instead of empty selection requirements.

---

### `TASK-06`: Gene Overview Card — Protein Length Display
- **Target File(s):** Main gene information header card.
- **Issue:** Gene length currently only displays `429 bp`. Users need to see protein length in amino acids (`aa`).
- **Requirements:**
  1. Retrieve protein length from metadata or calculate from coding sequence length:
     $$L_{aa} = \left\lfloor \frac{L_{bp} - 3}{3} \right\rfloor \quad \text{(excluding termination codon)}$$
     *(Note: If protein length is directly available in GFF/gene store, prefer the source of truth).*
  2. Update the `Length` display field in the overview panel:
     - Before: `Length: 429 bp`
     - After: `Length: 429 bp (142 aa)` OR provide two fields: `Genomic Length: 429 bp` | `Protein Length: 142 aa`.
- **Verification:**
  - View `mmpS5` (`Rv0677c`, 429 bp) $\rightarrow$ displays `429 bp (142 aa)`.

---

### `TASK-07`: Genomic Coordinates Table — Horizontal Overflow & Copyable Text
- **Target File(s):** Genomic Coordinates table stylesheet and JSX structure.
- **Issue:** Large deletions/insertions (long `Ref` strings) stretch columns, push subsequent columns off-screen without horizontal scroll, and CSS prevents text copying.
- **Requirements:**
  1. Wrap the table in a responsive overflow container:
     ```css
     .table-responsive-container {
       width: 100%;
       overflow-x: auto;
       -webkit-overflow-scrolling: touch;
     }
     ```
  2. Enforce explicit column constraints for sequence fields (`Ref`, `Alt`):
     ```css
     .seq-cell {
       max-width: 220px;
       white-space: nowrap;
       overflow: hidden;
       text-overflow: ellipsis;
       font-family: monospace;
     }
     ```
     Provide a full sequence popup or tooltip on hover/click for truncated strings.
  3. Ensure table cell text selection is enabled:
     ```css
     table, tr, td, th {
       user-select: text !important;
       -webkit-user-select: text !important;
     }
     ```
- **Verification:**
  - Navigate to `katG` row with large multi-base deletions (e.g., position `2,153,900`).
  - Verify that the `Alt` column and pagination controls remain accessible and table scrolls horizontally if necessary.
  - Verify that sequence text can be highlighted with the mouse and copied (`Ctrl+C` / `Cmd+C`).

---

### `TASK-08`: Reactive Two-Way Selection: Resistance Profile $\rightarrow$ Coordinate Analysis
- **Target File(s):** `DrugResistanceTable.tsx`, `GenomicCoordinatesTable.tsx`, `CoordinateAnalysis.tsx`.
- **Issue:** Clicking a row in the Drug Resistance Profile table does not update the Genomic Coordinates table or trigger the Coordinate Analysis card.
- **Requirements:**
  1. Define a shared selection hook or state: `const [selectedMutation, setSelectedMutation] = useAtom(selectedMutationAtom);`
  2. On clicking any row in the **Drug Resistance Profile** table:
     - Set `selectedMutation` to the clicked variant identifier.
     - Filter or auto-scroll the **Genomic Coordinates** table to the matching genomic row.
     - Trigger coordinate analysis calculation and populate the **Coordinate Analysis** card immediately.
- **Verification:**
  - Click on `p.Ser315Asn` in the Isoniazid table.
  - Confirm **Coordinate Analysis** immediately updates without requiring manual re-typing.

---

### `TASK-09`: Genome Browser — Prokaryotic De-eukaryotization
- **Target File(s):** Embedded Genome Browser config (e.g., JBrowse/IGV/custom track renderer), sequence export modal, sequence feature dropdown.
- **Issue:** The genome browser treats bacterial genomes like eukaryotes: showing separate redundant tracks for `gene` vs `CDS` and referencing "Introns".
- **Requirements:**
  1. **Collapse Feature Hierarchy:** In the track configuration, treat `gene` and `CDS` as identical. Collapse or merge subfeatures so that a single bacterial CDS/gene track is displayed.
  2. **Remove Intron Elements:**
     - Remove "Intron" options from the "show sequence feature" dropdown.
     - Remove "Intron" references from the sequence export dialog (modal next to "Copy HTML").
  3. **Preserve Flanking Sequences:** Retain and highlight adjustable upstream/downstream flanking sequence extraction (default: $\pm 500\text{ bp}$).
- **Verification:**
  - Open "show sequence feature" and the sequence modal. Verify no occurrence of the word "Intron" exists.
  - Verify upstream/downstream sequence extraction slider/input ($\pm 500\text{ bp}$) remains functional.

---

### `TASK-10`: Genome Browser — Interactive Neighbor Gene Navigation
- **Target File(s):** Genome browser event listener / feature click callback.
- **Issue:** Clicking a neighboring gene (e.g., clicking `Rv0678` while inspecting `mmpS5`) opens an isolated pop-up instead of changing the global page context to that gene.
- **Requirements:**
  1. Intercept feature `onClick` handler within the genome track canvas/SVG.
  2. Prevent opening a modal/pop-up window.
  3. Extract the clicked feature's `locus_tag` or `gene_name` (e.g., `Rv0678`).
  4. Call the primary navigation handler:
     ```typescript
     onFeatureClick: (feature) => {
       const geneId = feature.get('locus_tag') || feature.get('name') || feature.get('id');
       if (geneId) {
         navigateToGene(geneId);
       }
     }
     ```
  5. Ensure the entire page (Header Card, Drug Profile, Genomic Coordinates, and Browser viewport) re-renders for the newly selected gene.
- **Verification:**
  - View `mmpS5`. Click adjacent gene `Rv0678` directly in the browser track. The entire dashboard must switch to `Rv0678`.

---

### `TASK-11`: Genome Browser — Enriched Hover Tooltip
- **Target File(s):** Track tooltip / hover overlay renderer.
- **Issue:** Hovering over a gene displays only the ID, lacking quick functional annotation (similar to Mycobrowser).
- **Requirements:**
  1. Enhance the tooltip payload to fetch and render:
     - **Gene Symbol:** `gene_name` (e.g., `katG`)
     - **Locus Tag:** `locus_tag` (e.g., `Rv1907c`)
     - **Product:** `product` (e.g., `catalase-peroxidase KatG`)
     - **Functional Note:** `note` / `functional_category`
  2. Style the tooltip as a compact, structured floating card.
- **Verification:**
  - Hover over `katG` in the track. Verify the tooltip displays Gene Name, Locus Tag, Product, and Functional Note.

---

### `TASK-12`: Drug Resistance Profile — Full WHO Catalogue Schema
- **Target File(s):** `DrugResistanceTable.tsx`, catalogue data loader/types.
- **Issue:** Current table lacks essential WHO columns (`effect`, `Comment`, `CHANGES vs ver1`, `Relaxed thresholds simulation`, `Silent mutation`).
- **Requirements:**
  1. Extend the variant TypeScript interface:
     ```typescript
     interface WHOCatalogueVariant {
       mutation: string;
       tier: 1 | 2;
       confidence: string;
       effect: string; // e.g., missense_variant, frameshift
       comment?: string;
       changes_vs_ver1?: string;
       relaxed_thresholds_simulation?: string; // BDQ_Rv0678, CFZ_Rv0678, INH_katG, DLM_ddn/fbiA/fbiB/fbiC/fgd1/Rv2983
       silent_mutation?: boolean | string;
     }
     ```
  2. Add corresponding columns to the table.
  3. Apply visual styling:
     - `comment`: render subtle red text/badge if remarks exist.
     - `changes_vs_ver1`: render with red badge/text when indicating version changes.
  4. Provide a "Column Visibility" toggle dropdown to let users show/hide optional metadata columns.
- **Verification:**
  - Open `katG` resistance table. Confirm columns `Effect`, `Comment`, `CHANGES vs ver1`, `Relaxed thresholds simulation`, and `Silent mutation` are present and populate correctly.

---

### `TASK-13`: New Feature — Browse by Drug Navigation Module
- **Target File(s):** Navigation bar, `BrowseByDrugModal.tsx` / `BrowseByDrugPage.tsx`.
- **Issue:** Users have no entry point to browse catalogue mutations starting from a drug name.
- **Requirements:**
  1. Create a "Browse by Drug" dropdown or view containing all catalogue drugs:
     - First-line: Isoniazid, Rifampicin, Pyrazinamide, Ethambutol.
     - Second-line / New: Bedaquiline, Clofazimine, Delamanid, Linezolid, Fluoroquinolones (Levofloxacin, Moxifloxacin), Amikacin, etc.
  2. For each drug, list the associated catalogue genes:
     - Example Bedaquiline: `Rv0678`, `atpE`, `pepQ`.
     - Example Isoniazid: `katG`, `inhA`, `fabG1`, `ahpC`.
  3. Clicking any gene chip navigates the dashboard directly to that gene.
- **Verification:**
  - Click "Drugs" $\rightarrow$ select "Bedaquiline" $\rightarrow$ click `Rv0678`. The dashboard must transition to `Rv0678`.

---

### `TASK-14`: New Feature — Catalogue Overview & Summary Statistics
- **Target File(s):** New route/component: `src/pages/CatalogueSummary.tsx` or modal.
- **Issue:** No high-level summary tables summarizing the dataset (e.g., number of mutations per tier, gene distribution) based on Naila's thesis summary format.
- **Requirements:**
  1. Implement a summary table containing:
     - Gene list with associated drugs.
     - Total count of catalogued variants per gene.
     - Breakdown per evidence tier (Tier 1: Associated with Resistance, Tier 2, etc.).
     - Count of LoF (Loss of Function) mutations.
  2. Include aggregate totals at the footer of each summary table.
- **Verification:**
  - Navigate to "Catalogue Summary". Verify summary tables load valid numeric counts consistent with the WHO catalogue dataset.

---

### `TASK-15`: Branding, Attribution, Institutional Identity & Citations
- **Target File(s):** `Header.tsx`, `Footer.tsx`, `CiteModal.tsx`.
- **Issue:** Logo is undersized and unlinked; missing formal attribution to USP and LaPAM; missing citation instructions and license notice.
- **Requirements:**
  1. **Laboratory Logo:**
     - Enlarge the LaPAM logo in the header/navbar.
     - Wrap the logo with an external anchor tag linking to the official laboratory website.
  2. **USP Institutional Logo:**
     - Add a discreet, high-resolution University of São Paulo (USP) crest/logo alongside the lab logo or in the footer.
  3. **Attribution Text in Footer:**
     - Set footer text to:
       `"Developed by Fernando Falat, Laboratory of Applied Research in Mycobacteria (LaPAM), University of São Paulo, Brazil."`
  4. **Repository Links:**
     - Provide GitHub icons linking to both the personal repository and the official Laboratory organization repository.
  5. **Citation & License Notice:**
     - Add a visible `"How to Cite"` button in the header or top banner opening a modal with standard citation copy-paste buttons and BibTeX.
     - Add license indicator badge (e.g., MIT or appropriate open-source license) in the footer.
- **Verification:**
  - Verify logo scaling and clickable link to LaPAM.
  - Verify presence of USP logo and exact attribution string in footer.
  - Click "How to Cite" and confirm citation modal opens with formatted text.

---

## Implementation Notes

The repository is a **Python Dash** application, not a React/TypeScript one, so
the TypeScript/JSX snippets in this spec were treated as statements of intent
and implemented with the equivalent Dash constructs (callbacks, `dcc.Store`,
`dash_table.DataTable`, pattern-matching component ids).

### Where the implementation departs from the literal spec

- **`TASK-09` (de-eukaryotization)** is solved at the data level rather than by
  editing the browser's UI. The embedded JBrowse build is a pre-compiled bundle
  inside `dash-jbrowse`, and its sequence panel only offers intron options when
  a feature has `CDS` or `exon` subfeatures. `DataLoader.get_prokaryotic_gff3_path()`
  therefore serves the browser a flattened annotation — one gene-level feature
  per locus, no subfeatures — which removes the redundant gene/CDS pair and
  every intron option at the source, and leaves the ±500 bp up/downstream
  extraction in place. `assets/tbdashboard.js` additionally hides the intron
  field that the browser's settings dialog renders unconditionally. The
  trade-off is that JBrowse can no longer derive a protein sequence from
  subfeatures, so a **Sequence Retrieval** panel provides the CDS, its
  translation and adjustable flanks directly.
- **`TASK-10` and `TASK-11`** are delivered through a new interactive
  **Gene Neighbourhood** track (Plotly). `dash-jbrowse` exposes no feature-click
  or tooltip hook to Python, so the requested navigation and enriched tooltip
  could not be attached to the JBrowse canvas. The new track is also the
  prokaryote-correct view the spec asks for. Product and functional notes were
  added to the flattened annotation as well, so the JBrowse feature panel shows
  them too.

### Corrections to the spec's own details

- `katG` is **`Rv1908c`**, not `Rv1907c` as stated in `TASK-11`. `Rv1907c` is
  the adjacent gene.
- `dnaA` / `Rv0001`, given in `TASK-05` as a non-catalogue example, **is** in the
  WHO catalogue (graded for isoniazid). `Rv0002` / `dnaN` was used to verify the
  non-catalogue state instead.
- The catalogue master file repeats the `CHANGES vs ver1` header. The second
  column carries unrelated numeric codes and is dropped on load, so the schema
  in `TASK-12` is unambiguous.
- `TASK-14` conflates two different WHO concepts. The summary reports both: the
  gene **tier** (1 = established resistance gene, 2 = candidate) and the five
  **final confidence gradings**. Because a catalogue row is one drug-variant
  association, distinct variants and associations are counted separately.

### Not verified in a live browser

The JBrowse feature-detail sequence dropdown and its settings dialog were
verified by code path and by asserting the served annotation has no
subfeatures, not by clicking through them in a browser. Worth a manual check.

### Left for the repository owner

- `LAB_GITHUB_URL` in `layout.py` is `None`; set it to surface the laboratory
  organisation's repository icon.
- Drop the official crest at `assets/usp.png` to replace the typographic USP
  wordmark in the footer.
- There is no `LICENSE` file in the repository, although the README, manuscript
  and footer all state GPL-3.0.
