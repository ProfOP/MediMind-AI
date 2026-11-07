# MediMind AI Setup Guide

This guide is for running and demonstrating MediMind AI locally. The app is an educational prototype, not a medical service.

## Before You Start

- macOS or Windows with Python 3.11 installed. Python 3.11 is recommended because ChromaDB needs `onnxruntime`, which is not available for every Python version.
- Internet access for the initial package install and first local embedding-model download.
- Ollama is optional. Without it, you can still demonstrate the app using its clearly labelled fixed-response demo mode.

MediMind does not use a paid AI API. Do not enter real patient information.

## Install the Project

Open Terminal and go to the folder containing `app.py`. Replace the example path if you put the project somewhere else:

```bash
cd ~/Desktop/project
python3.11 -m venv .venv
mkdir -p .cache/pip .tmp .localhome
PIP_CACHE_DIR="$PWD/.cache/pip" TMPDIR="$PWD/.tmp" \
.venv/bin/python -m pip install -r requirements.txt
```

This installs Python packages inside `.venv`. The project-local cache directories keep package downloads and temporary files under the project folder.

### Windows (PowerShell)

Open PowerShell and change to the folder containing `app.py`:

```powershell
Set-Location "$HOME\Desktop\project"
py -3.11 -m venv .venv
New-Item -ItemType Directory -Force .cache\pip, .tmp, .localhome | Out-Null
$project = (Get-Location).Path
$env:PIP_CACHE_DIR = Join-Path $project ".cache\pip"
$env:TEMP = Join-Path $project ".tmp"
$env:TMP = $env:TEMP
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If the project is not in `Desktop\project`, replace the first path with your project folder. Python packages are installed in the project-local `.venv`.

## First Run

On the first knowledge search, Sentence Transformers downloads the `all-MiniLM-L6-v2` embedding model (about 90 MB). This download requires internet. It is cached under `data/models/` for later offline retrieval. The bundled medical reference files are already included; no external medical dataset is required.

Start the app from the project folder:

```bash
cd ~/Desktop/project
mkdir -p .localhome .cache .tmp
HOME="$PWD/.localhome" XDG_CACHE_HOME="$PWD/.cache" TMPDIR="$PWD/.tmp" \
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
.venv/bin/streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Open [http://127.0.0.1:8501](http://127.0.0.1:8501) in your browser. To stop the app, press `Ctrl+C` in the Terminal running Streamlit.

If port `8501` is already in use, change `--server.port 8501` to `--server.port 8502` and open `http://127.0.0.1:8502`.

### Windows (PowerShell)

Start the app from the project folder:

```powershell
Set-Location "$HOME\Desktop\project"
$project = (Get-Location).Path
New-Item -ItemType Directory -Force .localhome, .cache, .tmp | Out-Null
$env:HOME = Join-Path $project ".localhome"
$env:XDG_CACHE_HOME = Join-Path $project ".cache"
$env:STREAMLIT_CONFIG_DIR = Join-Path $project ".streamlit"
$env:TEMP = Join-Path $project ".tmp"
$env:TMP = $env:TEMP
$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS = "false"
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Open [http://127.0.0.1:8501](http://127.0.0.1:8501). Press `Ctrl+C` in PowerShell to stop the server. If port `8501` is busy, use `--server.port 8502` and open `http://127.0.0.1:8502`.

## Use Demo Mode

1. Open **Session settings** above the page navigation.
2. Turn on **Use labelled demo mode**.
3. Submit a general question on **Medical assistant**.
4. Expand **Agent execution and sources** to see which agents ran and which references were retrieved.

Demo mode returns fixed sample text. It does not call an AI model, and the answer is labelled accordingly. This is the recommended way to demonstrate the app if you have not set up Ollama.

## Optional: Enable Local AI with Ollama

Ollama is a separate local runtime and is not installed by the project setup above. Install Ollama using its official instructions, then use a project-local model directory. If Ollama's desktop app is already running a server, stop that instance before starting another one from Terminal.

In one Terminal window:

```bash
cd ~/Desktop/project
mkdir -p data/ollama/models
OLLAMA_MODELS="$PWD/data/ollama/models" ollama serve
```

In a second Terminal window:

```bash
cd ~/Desktop/project
OLLAMA_MODELS="$PWD/data/ollama/models" ollama pull smollm2:360m
```

Keep the first Terminal running, then launch Streamlit in another Terminal using the command in **First Run**. The app connects only to Ollama on your own computer at `127.0.0.1:11434`; it rejects remote model hosts. The configured model is `smollm2:360m`. If it is unavailable, the app shows an error and does not silently switch to a cloud service.

### Windows (PowerShell)

Install Ollama separately using its official Windows installer. If Ollama's tray application is already running a service, stop that service before starting a second one from PowerShell.

In one PowerShell window:

```powershell
Set-Location "$HOME\Desktop\project"
New-Item -ItemType Directory -Force data\ollama\models | Out-Null
$env:OLLAMA_MODELS = Join-Path (Get-Location).Path "data\ollama\models"
ollama serve
```

In a second PowerShell window:

```powershell
Set-Location "$HOME\Desktop\project"
$env:OLLAMA_MODELS = Join-Path (Get-Location).Path "data\ollama\models"
ollama pull smollm2:360m
```

Keep the first window open. Launch Streamlit from another PowerShell window using the Windows command in **First Run**.

## The Three Pages

- **Medical assistant:** ask general health questions, optionally include a selected profile, view agent execution status, and inspect sources.
- **Patient profile:** create or edit synthetic patient details. Submitting the form saves them to the local SQLite database. To save a chat, select a patient and confirm **Confirm saving this chat to patient history** in Session settings.
- **Knowledge base:** browse or filter the included references and try a local top-three retrieval search.

Patient profiles and saved consultations persist in `data/medimind.sqlite3`. The Chroma index persists in `data/chroma/`. Deleting these files removes the corresponding local data. Keep synthetic data in the demonstration; this prototype is not designed or secured for real medical records.

## Safety and Limitations

MediMind provides general healthcare information for educational purposes only. It does not diagnose, prescribe, recommend medication doses, or direct treatment changes. A basic emergency keyword check may advise contacting local emergency services, but it is not a complete emergency detector. Always contact a qualified healthcare professional for health concerns; contact local emergency services in an emergency.

## Troubleshooting

- **`No module named ...`:** confirm the project folder is the current directory and rerun the install command for your platform (`.venv/bin/python ...` on macOS, `.\.venv\Scripts\python.exe ...` on Windows).
- **ChromaDB or `onnxruntime` install error:** use Python 3.11 to create `.venv`, then repeat the install command.
- **Embedding model download fails:** check internet access, then retry the Knowledge Base search. The model is needed only for initial setup and is cached under `data/models/`.
- **Ollama is not reachable:** start Ollama and verify the model was pulled. Or turn on **Use labelled demo mode** for a fixed sample response.
- **Ollama reports a missing model:** pull `smollm2:360m` with `OLLAMA_MODELS` set to the project-local `data/ollama/models` folder. Use the command for your shell above.
- **Tests:** run `.venv/bin/python -m pytest -q` on macOS or `.\.venv\Scripts\python.exe -m pytest -q` on Windows. Tests mock model calls and do not require Ollama.