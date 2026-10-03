# Synthetic benchmark evidence

Eight corrected UTF-8 trials form the primary matched cohort: seven accepted, one missing-report failure. A separate common-runtime-clarification repair pair has two accepted reports and does not replace or pool with primary outcomes. Fourteen earlier trials are retained diagnostics, excluded from performance conclusions. Read [summary.json](summary.json) for denominators, limits, grades and metrics, and the [findings](../../../docs/BENCHMARK-BATCH1.md) for interpretation.

`commands.requested.jsonl` records CLI-requested text; `commands.jsonl` records bridge-received text/results. Corrected runs match exactly. Legacy differences are recorded per run. Full CLI traces remain private; their hashes are retained. `reviewer-receipt.json` preserves independent artifact observations with private paths replaced by public relative references.

`snapshots/candidate-source-bytes.json` stores exact public candidate bytes as base64 with hashes. `snapshots/benchmark-wave1-used.json` is the exact task pack used. These snapshots preserve working-file line endings independently of caller source labels. The old runtime snapshot exists only to diagnose the defect; use the current UTF-8 bridge for new evaluations.

Verify all evidence files from this directory using Python standard library:

```python
import hashlib, json
from pathlib import Path
root = Path('.')
manifest = json.loads((root / 'evidence-manifest.json').read_text(encoding='utf-8'))
for entry in manifest['files']:
    path = root / entry['path']
    assert path.is_file()
    assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'], entry['path']
print('All recorded bytes match')
```

Fixture identity/source/target values are synthetic task inputs. Consumers resolve their own values. No private portfolio data or credentials are included.
