# Research Verification

## Cardinal rule

**No URL appears in a lesson plan unless `scripts/verify_research.py` has returned `verified: true` for it in the current planning session.**

## What to verify

- Every URL cited in a plan (primary source, article, video, activity handout)
- Every author attribution that names a specific published work
- Every statistic or "fact" the model is tempted to pull from training

## What not to verify

- The teacher's template
- The teacher's calendar
- Content the teacher provided directly

## Protocol

1. Web-search candidate resources for the lesson
2. For each candidate URL, call `scripts/verify_research.py <url>`. The script:
   - Fetches with a 10-second timeout
   - Confirms HTTP 200
   - Extracts `<title>` and compares against the claimed title (fuzzy match)
   - Checks the domain against the allowlist (below)
3. Cite only URLs returning `verified: true`
4. Batch calls when possible. `verify_research.py --batch candidates.jsonl`
   runs them concurrently. The batch file is one JSON object per line —
   minimum `{"url": "..."}`, and preferably
   `{"url": "...", "claimed_title": "...", "why_relevant": "..."}` as
   produced by Step 5 of the planner skill. Raw-URL lines are accepted
   for backward compatibility but skip the title-match check that
   trusted domains would otherwise get.

## Domain allowlist (seed)

Maintained inside `verify_research.py` as `ALLOWLIST`. Starting set:

- `loc.gov`, `si.edu`, `archives.gov`, any `*.gov`
- `pbslearningmedia.org`, `nasa.gov`, `noaa.gov`, `nih.gov`, `cdc.gov`
- `khanacademy.org`, `commonlit.org`, `newsela.com`, `readworks.org`
- `edsitement.neh.gov`, `brainpop.com`
- Any `*.edu`
- `ted.com`, `teded.com`
- Major public-media: `npr.org`, `pbs.org`, `bbc.co.uk`

Unknown domains pass only if the page title exactly matches the claimed title AND the domain is not on a soft blocklist (user-generated content farms, YouTube aggregators, etc.).

## Fallbacks when verification fails

In priority order:

1. Drop the URL and keep the activity in generic terms
2. Replace with a verified equivalent from the allowlist
3. Tell the teacher: "No verified source found for X — please provide a link or we'll generalize."

Never fabricate, paraphrase a bad URL into a good-looking one, or cite "according to research" without a specific source.

## Session cache

Verified URLs are cached for 30 days at `~/Documents/Lesson Plan Magic/.cache/verify/`. Cache hits are free; skip re-fetching. Cache misses or expired entries re-fetch.

Since 0.2.2 the cache is keyed by `(url, claimed_title)` rather than
URL alone. A no-title verification cannot stand in for a later call
that supplies a title — if the title changes, the URL is re-fetched
and the title-match check runs again. This closes the hole where a
single "trusted-domain, no title" hit could make a URL look verified
for 30 days regardless of what title was later claimed against it.
