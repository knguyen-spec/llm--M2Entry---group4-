# Local evaluation on macOS

```bash
cd "$HOME/Desktop/llm--M2---group4-"

curl -fsSL https://ollama.com/install.sh | sh
ollama --version
ollama pull llama3.2:3b
```

Start Ollama in a separate terminal if it is not already running:

```bash
ollama serve
```

In the repository terminal, after the 30 cases have been reviewed and
appended to `evals/test_cases.csv`:

```bash
python3 -m src.run_local_evaluation
```

The script writes one row per local call and refuses to run if the file does
not contain exactly 30 cases.
