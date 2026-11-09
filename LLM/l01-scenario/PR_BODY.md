## What

Adds the L01 working foundation for Albert's Marketplace's prompt-driven
support-ticket classifier: the component definition, zero-shot prompt, ten
synthetic cases and decision record 0001.

## Why

Creates a realistic, reviewable starting point for the project before the
group replaces the synthetic cases with the course-approved ticket set and
runs the first measured prompt evaluation.

## How it was checked

The CSV has ten rows covering all seven labels, one ambiguous case and one
prompt-injection attempt. `checked_by` contains a balanced reviewer assignment,
but each named teammate must still inspect and confirm the rows before this is
reported as graded evidence. No API result or error rate is claimed by this PR.

## Checklist

- [x] No API key, `.env` file or secret
- [x] No measured figure is presented as completed evidence
- [ ] Every named teammate has checked their assigned rows
- [ ] `docs/component.md` updated with measured first-prompt results
- [ ] Reviewed by another group member
