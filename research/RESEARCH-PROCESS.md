# Research Process (Stage 1)

Stage 1 turns a field (for example, "emerging technologies in agentic
AI") into one evidence-graded research file. Stage 2 (the paper) argues
from that file and from nothing else; Stage 3 (the diagrams) plots the
placements the file records. If a claim is not in the research file
with a source, it does not reach the paper or the chart.

Output: one research file per study, built from
`research/research-template.md`. Never ship a filled research file in
this repo; studies live with the work that commissioned them.

## Step 1: Define the theme set

Pick 8 to 12 themes for the field. A theme is one technology, practice,
or product class that can be placed on a hype cycle on its own merits.

Rules for the set:

1. Themes are comparable in grain. Do not mix a whole field ("AI
   agents") with one feature of it ("agent memory") in the same set.
2. The set spans the maturity range actually present in the field, not
   the range that makes a tidy curve. If everything is early, the
   chart will show it; that is a finding, not a defect.
3. One theme may be a mature baseline class (the field's equivalent of
   conversational assistants) so readers can calibrate the rest
   against something already at the plateau.
4. Name themes the way practitioners name them, in two to four words.

Record the set and the date at the top of the research file before
gathering evidence, so later additions are visible as changes of scope.

## Step 2: Gather evidence per theme

For each theme, gather three things.

**State of the art.** What exists now, who ships it, and what is proven
in production versus shown in a demo. Distinguish a shipped product
with named production users from a launch announcement, a waitlist, and
a concept video; they are different states and the file must say which.

**Expectations signals (hype indicators).** Funding rounds and
valuations, launch announcements, analyst forecasts, conference and
media attention, vendor claims about capability and timelines.

**Reality signals (grounding indicators).** Production deployments with
named users, failure and cancellation reports, benchmark results from
named benchmarks, adoption survey numbers, pricing and usage evidence,
postmortems.

At least one concrete data point per theme where one is available: a
percentage, a deployment count, a named production user, a benchmark
score. If no concrete data point can be sourced for a theme, write
"no sourced data point found" in that section. An honest gap is usable
evidence; a plausible number is not.

## Step 3: Apply source discipline

1. **Primary sources first:** vendor documentation and release notes,
   standards bodies, peer-reviewed or preprint papers, official
   statistics. Reputable analyst and press coverage second. Social
   posts and content marketing are leads to verify, never evidence.
2. Every material claim carries its source: source name, URL, and the
   date of the source (or the date accessed, when undated).
3. Flag any source older than about six months as "possibly stale"
   next to the claim that rests on it. Fast-moving fields outdate
   their coverage quickly.
4. Label every material claim with one of three grades:
   - **VERIFIED:** independently confirmed (a primary document, an
     official record, or two independent reputable sources agreeing).
   - **REPORTED:** asserted by a vendor, a participant, or a single
     press source, and not independently confirmed.
   - **FORECAST:** an analyst or vendor prediction about the future.
     A forecast is never restated as a fact anywhere downstream.
5. Never invent numbers. No estimated percentages, no rounded guesses
   presented as statistics. If a number matters and cannot be sourced,
   the theme's confidence rating absorbs the gap (Step 4).
6. Report contradictions rather than averaging them. When two sources
   disagree, record both, with their dates and grades, and let the
   placement rationale say which the placement leans on and why.

## Step 4: Place each theme

Each theme gets four placement outputs, recorded in its section.

**Position t** in [0, 1] along the hype cycle curve, using the phase
bands the generator draws (see `reference/spec-reference.md`):

| Phase | t range | Reading |
|---|---|---|
| Innovation Trigger | 0.00 to 0.15 | A breakthrough or launch starts attention; no proven production use |
| Peak of Inflated Expectations | 0.15 to 0.35 | Expectations outrun delivery; early adopters and press pile in (peak point about 0.21) |
| Trough of Disillusionment | 0.35 to 0.60 | Failures and limits dominate; interest wanes; producers exit or pivot (floor about 0.45) |
| Slope of Enlightenment | 0.60 to 0.83 | Working uses accumulate quietly; second-generation products; conservative adopters return |
| Plateau of Productivity | 0.83 to 1.00 | Mainstream adoption; the theme is bought for results, not novelty |

Place by the balance of the signals, not by age. Working heuristics:

- Expectations high and production evidence thin: peak.
- Failure and cancellation reports accumulating faster than
  deployments: trough, wherever the theme started.
- Named production users growing, coverage turning boring: slope.
- Procurement routine, benefits documented, novelty gone: plateau.

**Rationale:** one line, tied to named evidence from Step 2 (for
example, "two named production deployments against a cancellation
rate reported at over 40 percent").

**Time to plateau:** one of "mainstream now", "less than 2 years",
"2 to 5 years", "5 to 10 years", "more than 10 years", or "obsolete
before plateau", with its basis stated (an adoption rate, a standards
timeline, a named forecast labeled FORECAST).

**Confidence:** high, medium, or low, by evidence quality: high needs
primary sources and at least one concrete data point; low means the
placement rests on REPORTED or FORECAST material alone. Say what
evidence would raise a low rating.

## Step 5: Write the cross-cutting findings

Close the file with 4 to 6 findings that span themes: where the field
as a whole sits on the curve, the dominant failure modes, the gaps
between the fastest and slowest themes, recurring causes (for example,
governance or evaluation lagging capability), and what would move
several placements at once. Each finding cites the theme sections it
rests on. Findings are synthesis, and are labeled as such; they do not
introduce new claims.

## Step 6: Assemble and self-check

Assemble the file from `research/research-template.md`, ending with
the summary table (theme | t | time to plateau | confidence). Before
handing the file to Stage 2, check:

1. Every material claim has a source name, URL, date, and grade.
2. Every theme has its data point, or an explicit "none found".
3. Stale flags are in place; no forecast is phrased as a fact.
4. Contradictions are recorded, not smoothed over.
5. Every placement has a rationale, a time to plateau with basis, and
   a confidence rating.
6. The summary table matches the per-theme sections exactly.
