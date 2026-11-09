# Apply this L01 bundle on your Mac

This bundle is a draft scenario. It does not include a key and it does not
replace teammate review. After downloading and unzipping it, the extracted
folder should be at `~/Downloads/l01-scenario`.

The commands below assume the repository is at
`~/Desktop/llm--M2---group4-`.

## 1. Create a branch from the latest `main`

```bash
cd ~/Desktop/llm--M2---group4-
git fetch origin --prune
git switch main
git pull --ff-only origin main
git switch -c l01-scenario-foundation
```

If that branch already exists, use this instead of the last command:

```bash
git switch l01-scenario-foundation
```

## 2. Copy the four repository files

```bash
BUNDLE="$HOME/Downloads/l01-scenario"

mkdir -p docs/decisions prompts evals
cp "$BUNDLE/docs/component.md" docs/component.md
cp "$BUNDLE/prompts/route_zero_shot.md" prompts/route_zero_shot.md
cp "$BUNDLE/evals/test_cases.csv" evals/test_cases.csv
cp "$BUNDLE/docs/decisions/0001-component-and-task.md" docs/decisions/0001-component-and-task.md
```

`README-team-row.md` is a snippet only. Do not add it as a new repository
file. Merge its row into the existing `README.md` after confirming every
member's real GitHub username.

## 3. Review before committing

```bash
git diff --check
git diff --stat
git diff -- docs/component.md prompts/route_zero_shot.md evals/test_cases.csv docs/decisions/0001-component-and-task.md
```

Confirm that each `checked_by` name is a different teammate from `written_by`.
The names currently mean “assigned reviewer”, not “review already completed”.

## 4. Commit and push

```bash
git add docs/component.md prompts/route_zero_shot.md evals/test_cases.csv docs/decisions/0001-component-and-task.md
git commit -m "Complete L01 classifier foundation"
git push -u origin l01-scenario-foundation
```

## 5. Open the pull request

With GitHub CLI:

```bash
gh pr create \
  --base main \
  --head l01-scenario-foundation \
  --title "Complete L01 classifier foundation" \
  --body-file "$BUNDLE/PR_BODY.md"
```

Request a review from Lynn-Aurea or Sereine. Do not merge your own PR.

Without GitHub CLI, open the repository on GitHub, select the pushed branch,
choose **Compare & pull request**, paste the contents of `PR_BODY.md`, and
request a review.
