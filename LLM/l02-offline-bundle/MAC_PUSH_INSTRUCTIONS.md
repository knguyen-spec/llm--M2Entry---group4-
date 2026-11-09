# Apply the offline L02 harness

Use this only after the L01 pull request has been approved and merged.

```bash
cd "$HOME/Desktop/llm--M2---group4-"
git switch main
git pull --ff-only origin main
git switch -c l02-offline-harness

BUNDLE="$HOME/Desktop/AlbertSchool Mines PSL/LLM/l02-offline-bundle"
mkdir -p src tests runs docs/decisions

cp "$BUNDLE/src/schema.py" src/schema.py
cp "$BUNDLE/src/llm.py" src/llm.py
cp "$BUNDLE/tests/test_llm.py" tests/test_llm.py
cp "$BUNDLE/runs/calls.csv" runs/calls.csv
cp "$BUNDLE/docs/decisions/0002-structured-output-and-retries.md" \
  docs/decisions/0002-structured-output-and-retries.md
```

Add the contents of `README-key-note.md` to the existing `README.md`; do not
create a second README or overwrite the existing project README.

Install the test dependencies if needed, then run only the offline tests:

```bash
python3 -m pip install "pydantic>=2,<3" "python-dotenv>=1,<2" pytest
LLM_MODE=offline python3 -m pytest -q tests/test_llm.py
```

Review the diff:

```bash
git diff --check
git diff --stat
git status
```

Commit and push:

```bash
git add src/schema.py src/llm.py tests/test_llm.py runs/calls.csv \
  docs/decisions/0002-structured-output-and-retries.md README.md
git commit -m "Add validated classifier boundary and offline tests"
git push -u origin l02-offline-harness
```

Open the PR without merging it yourself:

```bash
gh pr create \
  --base main \
  --head l02-offline-harness \
  --title "Add validated classifier boundary and offline tests" \
  --body-file "$BUNDLE/PR_BODY.md"
```
