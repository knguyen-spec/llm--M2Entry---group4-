# Local-surrogate evaluation note

The three strategies were run on the same 30 cases using the local model
`llama3.2:3b` through Ollama. The run date, token counts and latency are in
`runs/calls.csv`; per-strategy outputs are in `runs/results_zero_shot.csv`,
`runs/results_few_shot.csv` and `runs/results_cot.csv`.

These results measure local-model behaviour only. They are not production-
provider evidence. Live provider accuracy, token usage, latency and cost per
1,000 calls remain pending because no valid personal provider key was
available.

External API cost for the local run was €0. Electricity and hardware costs
were not measured. Do not use €0 as the production-provider cost.
