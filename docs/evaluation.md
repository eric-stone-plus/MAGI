# Residual Stress And Ablation Evaluation

MAGI evaluation uses pre-recorded, atomic claims. It does not infer quality from
agreement counts, prose similarity, or container count. The evaluator in
`magi/evaluation.py` performs no model calls.

## Evidence model

An evaluation fixture contains:

- an evidence catalog of `snapshot://` references and the atomic claims each
  item can support;
- a closed oracle claim set with severity, materiality, required status, an
  equivalence key, and acceptable evidence references;
- one or more evaluation arms containing pre-recorded findings;
- a pre-registered execution order and stopping policy.

The KING LOONG fixture is synthetic and de-identified at the artifact level. It
contains only numeric and procedural claims already present in the delivered
report. It does not copy source documents, media, credentials, or OneDrive
metadata into the repository.

## Metrics

Every arm reports:

- supported claim precision;
- material and high-risk recall;
- omitted required and high-risk claims;
- unsupported or non-entailing citations;
- severity downgrade drift;
- linked challenges to a concrete earlier finding;
- same-family repeated observations;
- false differences between findings with the same equivalence key;
- independent support separately from author-consistency observations.

Multiple profiles using one model family are repeated observations from one
family, not multiple independent families. A cross-review finding is novel only
when it adds a supported material claim that earlier independent arms did not
already contain. Rewording or translation does not count as novelty.

## Author-consistency boundary

If the model reviewing a result also authored the reference report, its output
must use `review_mode: author_consistency`. Such findings can verify internal
consistency but are excluded from `independent_supported_claim_ids` and cannot
act as an independent vote or increase a cross-family independence estimate.

## Stop policy

The default fixture uses these gates:

1. Stop after the baseline if material recall is at least 95%, high-risk recall
   and precision are 100%, unsupported findings are zero, and no severity
   downgrade exists.
2. Stop a profile arm when it adds no supported material claim. Also stop when
   more than half of its reported differences are equivalence-key false
   differences.
3. Stop a cross-review arm when it adds no supported material claim.
4. Fail closed on an unsupported claim, unknown citation, non-entailing
   citation, or invalid challenge target.
5. Stop once all required claims have independent support. Author-consistency
   observations do not satisfy this condition.

The model-call values are planning estimates only. The deterministic evaluator
uses zero tokens and can be run locally:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_residual_stress -v
```

One case cannot estimate a confidence ceiling or error correlation. Any claim
that MAGI improves reliability requires multiple pre-registered cases, human
claim adjudication, reported variance, and a held-out evaluation set.
