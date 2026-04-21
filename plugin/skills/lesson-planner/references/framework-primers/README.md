# Framework Primers

One markdown file per instructional framework. Load ONLY the primers that appear in the active subject's `frameworks` array in `config.yaml` — keeps runtime context lean.

## Included primers (v0.1)

| File | Framework ID | Summary |
|---|---|---|
| `swirl.md` | `swirl` | Speaking / Writing / Interacting / Reading / Listening — literacy across content areas. |
| `udl.md` | `udl` | Universal Design for Learning (CAST) — multiple means of engagement, representation, action/expression. |
| `5e.md` | `5e` | Engage / Explore / Explain / Elaborate / Evaluate (BSCS). |
| `siop.md` | `siop` | Sheltered Instruction Observation Protocol — content + language objectives. |
| `gradual-release.md` | `gradual-release` | I Do / We Do / You Do (Fisher & Frey). |
| `workshop-model.md` | `workshop-model` | Mini-lesson → practice → share. |
| `direct-instruction.md` | `direct-instruction` | Hunter's 7-step explicit instruction. |
| `project-based.md` | `project-based` | Driving question → public product (PBLWorks). |
| `marzano.md` | `marzano` | Nine high-yield instructional categories. |
| `hattie.md` | `hattie` | Effect-size-ranked influences on achievement. |

## Custom / district-specific frameworks

If the teacher's district uses a framework not in this list, they can upload the district's framework doc and set `subjects[].custom_framework_path` in config. The skill reads that doc at plan time and applies its vocabulary/structure.

## Structure of each primer

1. Overview (what it is, who created it, what problem it solves)
2. Core components / phases / principles
3. How it shapes a lesson plan
4. Language signals — words/phrases that indicate the framework is active
5. Common pitfalls
6. Authoritative source

Each primer is kept under 400 words so loading multiple at once stays cheap.
