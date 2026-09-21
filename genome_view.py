"""
Genome visualisation components.

Two complementary views are rendered:

* An interactive **gene neighbourhood track** built with Plotly. It is
  prokaryote-native (one feature per locus, no exon/intron machinery), every
  gene is clickable so the whole dashboard follows the selection (TASK-10),
  and hovering shows a structured functional annotation card (TASK-11).
* The embedded **JBrowse 2** linear view, for base-level inspection and
  sequence retrieval, fed with the flattened annotation (TASK-09).
"""
from typing import List, Optional

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html

from data_utils import GeneInfo

# Default flank shown around the active gene, and the choices offered.
DEFAULT_WINDOW_BP = 5000
WINDOW_CHOICES = [
    {"label": "± 1 kb", "value": 1000},
    {"label": "± 5 kb", "value": 5000},
    {"label": "± 10 kb", "value": 10000},
    {"label": "± 25 kb", "value": 25000},
]

# Default flank for sequence retrieval, matching the JBrowse default.
DEFAULT_FLANK_BP = 500

# Pattern-matching id: the track only exists once a gene is loaded, and a
# plain string id would break every callback that reads its clickData.
GENE_TRACK_ID = {"type": "gene-track", "index": "main"}

COLOR_ACTIVE = "#438E8E"
COLOR_FORWARD = "#9CCBCB"
COLOR_REVERSE = "#C9D8E4"
COLOR_NONCODING = "#E3C9A8"

_MAX_NOTE_CHARS = 220


def _wrap(text: str, width: int = 58) -> str:
    """Soft-wrap text with HTML breaks for use inside a Plotly tooltip."""
    words = str(text).split()
    lines: List[str] = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 > width:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    return "<br>".join(lines)


def _hover_card(gene: GeneInfo, is_active: bool) -> str:
    """
    Structured hover annotation for one gene (TASK-11).

    Shows the gene symbol, locus tag, product and functional note, in the
    style of a compact Mycobrowser-like summary card.
    """
    rows = [
        f"<b>{gene.display_name}</b>"
        + ("  <i>(current gene)</i>" if is_active else ""),
        f"<b>Locus tag:</b> {gene.locus_tag}",
    ]
    if gene.product:
        rows.append(f"<b>Product:</b> {_wrap(gene.product)}")
    if gene.biotype and gene.biotype != "protein_coding":
        rows.append(f"<b>Biotype:</b> {gene.biotype.replace('_', ' ')}")

    coordinates = f"{gene.start:,}–{gene.end:,} ({gene.strand}) · {gene.length:,} bp"
    if gene.protein_length:
        coordinates += f" · {gene.protein_length:,} aa"
    rows.append(f"<b>Position:</b> {coordinates}")

    if gene.note:
        note = gene.note
        if len(note) > _MAX_NOTE_CHARS:
            note = note[:_MAX_NOTE_CHARS].rstrip() + "…"
        rows.append(f"<b>Note:</b> {_wrap(note)}")

    rows.append("<i>Click to open this gene</i>")
    return "<br>".join(rows)


def _gene_color(gene: GeneInfo, is_active: bool) -> str:
    if is_active:
        return COLOR_ACTIVE
    if not gene.is_protein_coding:
        return COLOR_NONCODING
    return COLOR_FORWARD if gene.strand == "+" else COLOR_REVERSE


def build_neighborhood_figure(
    genes: List[GeneInfo],
    active_gene: GeneInfo,
    window_start: int,
    window_end: int,
) -> go.Figure:
    """
    Build the clickable gene neighbourhood track.

    Forward-strand genes sit on the upper row and reverse-strand genes on the
    lower row. ``customdata`` carries the locus tag of each gene so the click
    callback can navigate the dashboard.
    """
    figure = go.Figure()

    bases, spans, rows, colors, hovers, custom, labels = [], [], [], [], [], [], []
    arrow_x, arrow_y, arrow_symbols, arrow_colors = [], [], [], []

    for gene in genes:
        is_active = gene.locus_tag == active_gene.locus_tag
        visible_start = max(gene.start, window_start)
        visible_end = min(gene.end, window_end)
        color = _gene_color(gene, is_active)
        row = 1 if gene.strand == "+" else 0

        bases.append(visible_start)
        spans.append(max(visible_end - visible_start, 1))
        rows.append(row)
        colors.append(color)
        hovers.append(_hover_card(gene, is_active))
        custom.append(gene.locus_tag)

        # Only label genes wide enough for the text to fit legibly.
        span_fraction = (visible_end - visible_start) / max(window_end - window_start, 1)
        labels.append(gene.display_name if span_fraction > 0.045 else "")

        # Direction marker at the gene's 3' end.
        arrow_x.append(gene.end if gene.strand == "+" else gene.start)
        arrow_y.append(row)
        arrow_symbols.append("triangle-right" if gene.strand == "+" else "triangle-left")
        arrow_colors.append(color)

    figure.add_trace(go.Bar(
        base=bases,
        x=spans,
        y=rows,
        orientation="h",
        width=0.42,
        marker={"color": colors, "line": {"color": "#FFFFFF", "width": 1}},
        text=labels,
        textposition="inside",
        insidetextanchor="middle",
        textfont={"size": 11, "color": "#1F2933"},
        customdata=custom,
        hovertext=hovers,
        hovertemplate="%{hovertext}<extra></extra>",
        showlegend=False,
        cliponaxis=False,
    ))

    figure.add_trace(go.Scatter(
        x=arrow_x,
        y=arrow_y,
        mode="markers",
        marker={
            "symbol": arrow_symbols,
            "size": 11,
            "color": arrow_colors,
            "line": {"color": "#FFFFFF", "width": 1},
        },
        customdata=custom,
        hovertext=hovers,
        hovertemplate="%{hovertext}<extra></extra>",
        showlegend=False,
    ))

    # Highlight the active gene's span across the whole track.
    figure.add_vrect(
        x0=active_gene.start,
        x1=active_gene.end,
        fillcolor=COLOR_ACTIVE,
        opacity=0.08,
        line_width=0,
        layer="below",
    )

    figure.update_layout(
        barmode="overlay",
        bargap=0.1,
        height=210,
        margin={"l": 8, "r": 8, "t": 28, "b": 36},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        clickmode="event",
        dragmode=False,
        hoverlabel={
            "bgcolor": "#FFFFFF",
            "bordercolor": COLOR_ACTIVE,
            "font": {"size": 12, "color": "#2D3748", "family": "Inter, sans-serif"},
            "align": "left",
        },
        xaxis={
            "range": [window_start, window_end],
            "title": {"text": f"{active_gene.chromosome} position (bp)", "font": {"size": 11}},
            "tickformat": ",d",
            "showgrid": True,
            "gridcolor": "#F1F5F9",
            "zeroline": False,
            "fixedrange": True,
        },
        yaxis={
            "range": [-0.55, 1.55],
            "tickmode": "array",
            "tickvals": [0, 1],
            "ticktext": ["− strand", "+ strand"],
            "showgrid": False,
            "zeroline": False,
            "fixedrange": True,
            "tickfont": {"size": 11},
        },
    )
    return figure


def neighborhood_card(
    genes: List[GeneInfo],
    gene_info: GeneInfo,
    window_bp: int = DEFAULT_WINDOW_BP,
) -> dbc.Card:
    """Card wrapping the interactive neighbourhood track."""
    window_start = max(1, gene_info.start - window_bp)
    window_end = gene_info.end + window_bp
    figure = build_neighborhood_figure(genes, gene_info, window_start, window_end)

    return dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col(
                    html.H5(
                        [html.I(className="bi bi-diagram-3 me-2"), "Gene Neighbourhood"],
                        className="card-header-title",
                    ),
                    md=6,
                ),
                dbc.Col([
                    dbc.RadioItems(
                        id="neighborhood-window",
                        options=WINDOW_CHOICES,
                        value=window_bp,
                        inline=True,
                        className="window-toggle",
                        inputClassName="btn-check",
                        labelClassName="btn btn-sm window-toggle-btn",
                        labelCheckedClassName="active",
                    )
                ], md=6, className="text-md-end"),
            ], align="center"),
        ], className="card-header-custom"),
        dbc.CardBody([
            html.P([
                html.I(className="bi bi-cursor me-2"),
                "Click any gene to load it. Hover for product and functional annotation.",
            ], className="text-muted small mb-2"),
            dcc.Graph(
                id=dict(GENE_TRACK_ID),
                figure=figure,
                config={"displayModeBar": False, "doubleClick": False},
                className="neighborhood-graph",
            ),
            html.Div([
                _legend_swatch(COLOR_ACTIVE, "Current gene"),
                _legend_swatch(COLOR_FORWARD, "Forward strand"),
                _legend_swatch(COLOR_REVERSE, "Reverse strand"),
                _legend_swatch(COLOR_NONCODING, "Non-coding (rRNA/tRNA/ncRNA)"),
            ], className="d-flex flex-wrap gap-3 mt-2 small text-muted"),
        ]),
    ], className="result-card")


def _legend_swatch(color: str, label: str) -> html.Span:
    return html.Span([
        html.Span(className="legend-swatch", style={"backgroundColor": color}),
        label,
    ], className="d-inline-flex align-items-center")


def jbrowse_card(jbrowse_component, gene_info: GeneInfo, flank: int) -> dbc.Card:
    """Card wrapping the embedded JBrowse 2 linear genome view."""
    return dbc.Card([
        dbc.CardHeader([
            html.H5(
                [html.I(className="bi bi-eye me-2"), "Genomic Visualization"],
                className="card-header-title",
            )
        ], className="card-header-custom"),
        dbc.CardBody([
            html.Div(jbrowse_component, className="jbrowse-container"),
            html.P([
                html.I(className="bi bi-info-circle me-2"),
                f"Showing {gene_info.chromosome}:"
                f"{max(1, gene_info.start - flank):,}–{gene_info.end + flank:,} "
                f"({flank:,} bp flanking). The annotation track is flattened to one "
                "feature per locus: in ",
                html.I("M. tuberculosis"),
                " a CDS is the gene, so no separate CDS track or intron controls are shown.",
            ], className="text-muted small mb-0 mt-3"),
        ]),
    ], className="result-card")


def sequence_card(gene_info: GeneInfo) -> dbc.Card:
    """
    Sequence retrieval panel.

    Replaces the browser's eukaryotic "gene w/ introns" options with the two
    that are meaningful for a bacterium — the coding sequence and its protein
    translation — while keeping adjustable upstream/downstream flanking
    extraction at the ±500 bp default (TASK-09).
    """
    options = [
        {"label": "Coding sequence (CDS = gene)", "value": "cds"},
        {"label": "CDS + flanks", "value": "cds_flank"},
        {"label": "Upstream flank only", "value": "upstream"},
        {"label": "Downstream flank only", "value": "downstream"},
    ]
    if gene_info.is_protein_coding:
        options.insert(2, {"label": "Protein translation", "value": "protein"})

    return dbc.Card([
        dbc.CardHeader([
            html.H5(
                [html.I(className="bi bi-code-square me-2"), "Sequence Retrieval"],
                className="card-header-title",
            )
        ], className="card-header-custom"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Sequence", className="small text-muted mb-1"),
                    dbc.Select(id="sequence-kind", options=options, value="cds", size="sm"),
                ], md=5),
                dbc.Col([
                    dbc.Label("Flanking bases (± bp)", className="small text-muted mb-1"),
                    dbc.Input(
                        id="sequence-flank",
                        type="number",
                        value=DEFAULT_FLANK_BP,
                        min=0,
                        max=10000,
                        step=50,
                        size="sm",
                    ),
                ], md=4),
                dbc.Col([
                    dbc.Label(" ", className="small d-block mb-1"),
                    html.Div([
                        dcc.Clipboard(
                            id="sequence-clipboard",
                            title="Copy sequence",
                            className="copy-btn",
                        ),
                        html.Span("Copy", className="small text-muted ms-1"),
                    ], className="d-flex align-items-center"),
                ], md=3),
            ], className="g-2 align-items-end"),
            html.Div(id="sequence-meta", className="small text-muted mt-3"),
            html.Pre(id="sequence-output", className="sequence-output mt-2"),
        ]),
    ], className="result-card")


def format_sequence(sequence: str, block: int = 10, per_line: int = 60) -> str:
    """Format a sequence into spaced blocks for readable, copyable output."""
    if not sequence:
        return ""
    lines = []
    for offset in range(0, len(sequence), per_line):
        chunk = sequence[offset:offset + per_line]
        blocks = " ".join(chunk[i:i + block] for i in range(0, len(chunk), block))
        lines.append(f"{offset + 1:>9,}  {blocks}")
    return "\n".join(lines)


def neighbor_navigation(
    previous: Optional[GeneInfo], following: Optional[GeneInfo]
) -> html.Div:
    """Previous/next gene shortcuts for keyboard-free neighbourhood browsing."""
    def button(gene: Optional[GeneInfo], direction: str) -> dbc.Button:
        if gene is None:
            return dbc.Button("—", size="sm", disabled=True, className="neighbor-btn")
        icon = "bi-chevron-left" if direction == "prev" else "bi-chevron-right"
        content = [html.I(className=f"bi {icon} me-1"), gene.display_name]
        if direction == "next":
            content = [gene.display_name, html.I(className=f"bi {icon} ms-1")]
        return dbc.Button(
            content,
            id={"type": "neighbor-link", "index": gene.locus_tag},
            size="sm",
            className="neighbor-btn",
            title=f"{gene.display_name} ({gene.locus_tag}) · {gene.product or 'no product'}",
        )

    return html.Div([
        html.Span("Neighbouring genes:", className="text-muted small me-2"),
        button(previous, "prev"),
        button(following, "next"),
    ], className="d-flex align-items-center gap-2 flex-wrap")
