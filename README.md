# Algorithm Reverse Engineer

**English** | [简体中文](README.zh-CN.md)

A reusable Codex skill that traces an algorithm's implementation, reconstructs its language-independent computational process, and checks that reconstruction against the code.

The goal is an accurate algorithm baseline: explain what the selected implementation actually computes, with enough detail for a domain researcher to understand it and, where evidence permits, build a behaviorally equivalent version.

## What it does

Given a Git repository URL or a local repository path, the skill:

1. **Fixes the analysis scope** — records the commit, local changes, entry points, effective configuration, dependencies, and accessible resources.
2. **Traces the implementation** — follows execution and data flow through wrappers, dispatch, core operations, and postprocessing.
3. **Reconstructs the algorithm** — organizes the computation by mathematical purpose, with representations, formulas, stages, and complete pseudocode.
4. **Verifies the reconstruction** — maps conclusions back to source evidence, searches for counterexamples, and runs small checks when practical.

It is intended for numerical methods, machine learning, computer vision, graphics, geometry, optimization, search, and mixed pipelines. It does not assume a particular language, framework, or Git host. A function call graph is not treated as an algorithm explanation.

## Quick start

The entry point is [SKILL.md](SKILL.md). Give Codex its local path and an analysis request. If the skill is already available by name in your environment, invoke it with `$algorithm-reverse-engineer`.

Accepted inputs:

| Input | Required? |
|---|---|
| Git remote URL or local repository path | Yes |
| Branch, tag, or commit | Optional |
| Target algorithm, module, entry point, command, configuration, or scenario | Optional |
| Output directory | Optional; preferably outside the analyzed repository |
| Existing engineering analysis report | Optional; checked before reuse |

Reports default to **Chinese**; request English explicitly if preferred. The English default of this README does not change the skill's report language.

### Analyze a remote repository

```text
$algorithm-reverse-engineer
Analyze https://github.com/karpathy/micrograd.git.
Scope: the training path in demo.ipynb and the core computations it uses.
Pin and record the retrieved commit. Write the reports in English to
../reports/micrograd. Complete implementation analysis, algorithm reconstruction,
and reverse verification; use only small validation inputs.
```

### Analyze a local working tree

```text
$algorithm-reverse-engineer
Analyze ./solver using run.py and configs/demo.json.
Preserve uncommitted changes and determine the effective configuration.
Reconstruct the mathematics and full pseudocode, then check them against the code.
Write English reports to ../reports/solver.
```

### Continue from an existing report

```text
$algorithm-reverse-engineer
Repository: ./matcher
Existing report: ../reports/matcher/01-engineering.md
Check its version, configuration, and key evidence. Reuse reliable findings,
fill gaps, and continue algorithm reconstruction and reverse verification.
Write English reports to ../reports/matcher-final.
```

## What you get

Three linked Markdown reports keep implementation evidence separate from the independently readable algorithm explanation:

| Report | Contents |
|---|---|
| `01-engineering.md` | Source identity, scope, configuration, execution paths, data contracts, evidence index, and open questions |
| `02-algorithm.md` | Problem definition, core idea, meaningful flow diagrams, stage breakdown, mathematics, full pseudocode, design decisions, and minimum reproduction requirements |
| `03-verification.md` | Reverse checks, actual test results, counterexamples, verification boundaries, and cleanup status |

The final checks ask whether the explanation remains concrete after removing repository-specific names, and whether a reimplementation still requires guessing essential details.

## Evidence and limits

- Distinguishes source facts, actual runs, documentation claims, inferences, and unresolved questions.
- Preserves mechanisms that affect results: configuration overrides, precision, ordering, randomness, state reuse, thresholds, stopping rules, and output mappings.
- Separates independent mathematical checks, extracted original functions, compatibility-adapted models, and complete project runs.
- Records missing source, dependencies, weights, or dynamic behavior as explicit gaps. Static consistency is not proof of correctness.
- Preserves local changes and uses isolated copies for other versions. Full training, large data downloads, code refactoring, algorithm improvements, and broad literature surveys are outside the default scope.

## Validation experience

The skill has been exercised on selected paths in nine projects, with different levels of runtime coverage:

| Cases | Coverage |
|---|---|
| micrograd, FuzzyWuzzy | Small execution and differential checks, including configuration and unused-implementation traps |
| scikit-image Canny, scikit-learn KMeans | Core numerical and discrete-output comparisons; Canny retains unresolved pixel differences |
| tinyrenderer, PyTorch MNIST example | Static analysis plus translated checks for rendering; MNIST remained a partial static analysis |
| Annotated Transformer | Independent mathematical checks and extracted PyTorch definitions, including a tiny forward pass and one optimizer step |
| PointNet | Original modules with explicit TensorFlow compatibility adapters; a small training step and state checks |
| Darknet YOLOv3-tiny | Extracted native C operations and configuration checks; a later DLL reload was blocked by Windows application control |

These are scoped trials, not claims of full-repository recovery, full training, or universal equivalence. Local validation reports and the test environment are excluded from Git.

## Repository layout

```text
SKILL.md             Core workflow, evidence rules, and completion criteria
agents/openai.yaml   Skill display metadata
references/          Guidance loaded as needed
assets/              Three report templates
scripts/             Optional deterministic evidence helpers
```

The helpers require **Python 3.8+ and Git**; they do not require machine-learning frameworks. Dependencies for running a target project are separate.

From this skill directory, with outputs outside the target repository:

```sh
python scripts/repo_snapshot.py /path/to/repository --output /path/to/reports/snapshot.json
python scripts/check_evidence.py --repo /path/to/repository --evidence /path/to/reports/evidence.json
```

The snapshot records Git identity and local changes. The evidence checker validates commit identity, paths, line ranges, and file hashes; it cannot determine whether a conclusion is semantically supported. See the [evidence format and verification guidance](references/verification.md).
