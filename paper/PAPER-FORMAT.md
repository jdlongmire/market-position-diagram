# Paper Format (Stage 2)

Stage 2 turns a Stage 1 research file into a paper. The format is a
standing ruling, not a preference of this skill: **whitepapers and
papers are built as journal articles with magazine polish.** Not an
essay whitepaper (title, prose, no apparatus) and not a research
report (internal report title, summary verdicts, numbered findings,
registers); the report format is reserved for research dossiers.

## The format elements

Every paper carries all of these, in this order:

1. **Kicker:** a short uppercase subject line (field, then topic).
2. **Display title.**
3. **Deck:** one italic sentence under the title stating the claim.
4. **Byline:** author names in uppercase, then a dateline (month and
   year), then the line "Human-Curated, AI-Enabled (HCAE)". Follow
   the byline and About the Authors treatment of the agentic
   enterprise article (the model named under "Template" below).
5. **Abstract:** one paragraph, labeled "Abstract", covering the
   field, the method, the headline placements, and the main finding.
6. **Keywords:** one line, labeled "Keywords", five to eight terms.
7. **Numbered sections** (1., 2., 3., ...), titled, arguing in prose.
8. **Figures** with numbered captions ("Figure 1.", "Figure 2."),
   each caption saying what the figure shows and where its data
   comes from. Figures are rendered by the Stage 3 generators and
   embedded as images.
9. **Tables** with numbered captions ("Table 1.", "Table 2.") and a
   header row; the placement summary table is normally Table 1.
10. **Pull quote:** one sentence from the paper's own argument, set
    off between rules at the point it summarizes.
11. **References:** numbered [1], [2], ..., naming each source and
    linking the original. Primary sources the placements rest on are
    listed individually, not bundled.
12. **About the Authors:** a closing note with author bios and the
    HCAE statement.

## Structure: building the paper on the research file

The paper argues the research file's placements; it introduces no
claim the file does not carry. Standard structure:

1. **Introduction.** The field, why its expectations matter now, the
   method in one paragraph (theme set, evidence discipline, placement
   scale), and the headline result.
2. **One section per phase or theme cluster.** Group the themes by
   curve position (for example: "At the peak", "In the trough",
   "Climbing the slope") or run one section per theme when the set is
   small. Each section argues its placements from the evidence:
   state of the art, the signal balance, the data points. Claims keep
   their research-file grades in the prose; a FORECAST is phrased as
   a forecast ("Gartner predicts..."), never absorbed into the
   paper's own voice as fact.
3. **The placement table.** Table 1 reproduces the research file's
   summary table (theme, t, time to plateau, confidence) unchanged.
   If the paper's Figure 1 is the hype cycle chart, it sits with this
   section or the introduction, captioned to name the research file
   as its source.
4. **Cross-cutting findings.** The research file's findings, argued
   as the paper's synthesis.
5. **Limitations.** What the evidence could not settle: thin themes
   and their low confidence ratings, stale sources, contradictions
   left unresolved, and the judgment inherent in any placement.
   Stated plainly, in the open.
6. **Conclusion.** What the placements mean for a reader deciding
   where to spend attention or money, kept inside what the evidence
   supports.
7. **References** and **About the Authors** close the paper.

## Template

Start from `paper/article-template.html`: a working HTML article with
embedded CSS implementing every element above, modeled on the agentic
enterprise article's stylesheet (centered front matter, serif body,
labeled abstract and keywords, drop cap on the introduction, ruled
pull quote, captioned figures and tables, hanging-indent references,
ruled About the Authors block, running footer with page numbers).
Slots to fill are marked `<<LIKE THIS>>`. Replace every slot; never
ship a paper with a slot left in.

## Build pipeline

- **HTML is the source of record.** Write and revise the `.html`;
  derive everything else from it.
- **PDF:** WeasyPrint, from the docs venv:
  `~/workspace/.venvs/docs/bin/python -m weasyprint paper.html paper.pdf`
  Run it from the paper's directory so figure paths resolve.
- **DOCX:** pandoc, from the pandoc venv
  (`~/workspace/.venvs/pandoc/bin/python` with pypandoc, or the pandoc
  binary it bundles): `pandoc paper.html -o paper.docx`, figures
  embedded from local image files.
- **Figures:** render the charts first with the Stage 3 generators
  (`scripts/make_hypecycle.py`, `scripts/make_quadrant.py`) and embed
  their PNG output. The PPTX stays the editable master of each chart;
  the paper embeds the render.
- **QA before delivery:** build the PDF, render its pages to PNG
  (`pdftoppm -png -r 100`), and view them. Confirm every format
  element is present, figures and captions sit together, no caption
  is orphaned at a page foot, tables are not split awkwardly, and no
  `<<...>>` slot survives. Do not deliver a paper you have not viewed
  as rendered pages.
