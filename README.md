# AutoGen Financial Writer

A Streamlit app that runs a small AutoGen workflow with three agents:

- Financial assistant
- Research assistant
- Writer

The app asks the agents to gather financial context, investigate possible reasons for stock movement, and draft a blog-style response from the results.

## Project Files

- `ss.py` - Main Streamlit app.
- `run_app.bat` - Recommended Windows launcher. Uses the local `myenv` Python environment.
- `run_app.ps1` - PowerShell launcher. May be blocked by Windows execution policy.
- `.vscode/settings.json` - Points VS Code to the project virtual environment.
- `.env` - Local environment variables. Do not commit or share this file.

## Requirements

This project expects dependencies to be installed in the local virtual environment:

```bat
myenv\Scripts\python.exe
```

Important packages include:

- `autogen`
- `ag2`
- `streamlit`
- `python-dotenv`
- `openai`

## Environment Variables

Create or update `.env` with:

```env
OPENAI_API_KEY=your_openai_api_key_here
OAI_CONFIG_LIST=[{"model":"gpt-4","api_key":"${OPENAI_API_KEY}"}]
```

Keep `.env` private because it contains your API key.

## Run The App

From this folder, run:

```bat
.\run_app.bat
```

Then open the local Streamlit URL shown in the terminal, usually:

```text
http://localhost:8501
```

## Why Use `run_app.bat`?

On this machine, the plain `streamlit` command points to Anaconda, but `autogen` is installed inside this project's `myenv`.

Using `run_app.bat` avoids the common error:

```text
ModuleNotFoundError: No module named 'autogen'
```

It does this by running Streamlit through:

```bat
myenv\Scripts\python.exe -m streamlit run ss.py
```

## Quick Checks

Verify that AutoGen imports correctly:

```bat
myenv\Scripts\python.exe -c "import autogen; print(autogen.__version__)"
```

Verify the app syntax:

```bat
myenv\Scripts\python.exe -m py_compile ss.py
```
