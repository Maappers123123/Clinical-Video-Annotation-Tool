# 🎬 Clinical Video Annotation Tool

A desktop tool for annotating clinical videos (e.g. Dyskinesia Impairment
Scale (DIS) / Barry-Albright Dystonia Scale (BADS) scoring) on a per-window or
per-video basis, with CSV score export and optional annotated MP4
export.

## 📁 Contents

```
requirements.txt   Python package dependencies
run.bat             Installer + launcher for Windows
run.sh              Installer + launcher for macOS / Linux
scorer.py           The application itself
```

You do **not** need to install anything manually beyond Python itself:
`run.bat` / `run.sh` will set everything else up automatically the first
time you run them.

---

## ⚙️ 1. Installation

### Step 1: Install Python (one-time, skip if already installed)

1. Go to <https://www.python.org/downloads> and download Python 3.10 or
   newer.
2. Run the installer. **⚠️ On the very first screen, check the box "Add
   python.exe to PATH"** before clicking Install. This step is easy to
   miss and is the most common cause of installation problems.
3. If you use Anaconda/Miniconda instead of a standalone Python
   install, see the **Anaconda / Miniconda users** note below.

### Step 2: Run the setup script

**Windows:** double-click `run.bat`.

**macOS / Linux:** open a terminal in this folder and run:
```
chmod +x run.sh     # first time only, makes the script executable
./run.sh
```

The first run will:
- create a local, self-contained Python environment in a new `.venv`
  folder (this does **not** touch your system Python, see note below),
- install all required packages into that environment,
- launch the application.

Every run after that reuses the same `.venv` and starts much faster,
since the packages are already installed. If you ever want to force a
completely clean reinstall, just delete the `.venv` folder and run the
script again.

> **🔐 Is this safe for my system Python / Anaconda install?**
> Yes. Everything the script installs goes into the local `.venv`
> folder only, never into your system-wide or Anaconda Python. Deleting
> `.venv` removes 100% of what the script has ever installed, with zero
> side effects elsewhere on your computer.

### Anaconda / Miniconda users

If Python was installed via Anaconda/Miniconda rather than the
standalone python.org installer, `run.bat` can only see it if it is
launched from a terminal where that conda environment is already
active:

1. Open **Anaconda Prompt** from the Start menu (not a plain
   Command Prompt / PowerShell window).
2. Navigate to this folder, e.g.:
   ```
   cd C:\path\to\this\folder
   ```
   (Tip: drag the folder from File Explorer into the terminal window to
   auto-fill the correct path.)
3. Run the script:
   ```
   run.bat
   ```
   In PowerShell specifically, type `.\run.bat` (with the leading
   `.\`) instead of `run.bat`.

---

## 🖱️ 2. Using the application

### 🛠️ Step 1: Configure the session

On launch you'll see a configuration screen where you choose:

- **Project preset**: a ready-made configuration (e.g. QUOVADYS, DIS,
  BADS, UMC, DIS + BADS), or "None" to configure everything manually.
- **Point scale**: 3-point (0–2) or 5-point (0–4) scoring.
- **Timing mode**: score every 5-second window of the video, or score
  the full video at once.
- **Body scoring mode**: score the whole body together, or each body
  part separately.
- **Clinical scale type**: Dyskinesia Impairment Scale (DIS) and/or
  Barry-Albright Dystonia Scale (BADS), with sub-options for which
  movement type to score under DIS (dystonia, choreoathetosis, or
  both).
- **Saving options**: whether to save a CSV score file and/or export
  an annotated MP4 with the scores burned in.

The **Body Parts to Score** list on the right updates automatically
based on your preset/scale selection.

Click **Start Annotation Session** to continue.

### 🎞️ Step 2: Select videos

- **Add MP4 files** to pick one or more videos individually, or
  **Add folder** to add every MP4 in a folder at once.
- Use **Remove selected** / **Clear list** to adjust your selection.
- Click **Start Annotation** when your video list is ready.

### ✅ Step 3: Annotate

For each video (and, in window mode, each 5-second segment):

- Watch the clip, then click the score button matching your
  assessment for each scored body part/movement.
- **↻ Replay** re-plays the current segment.
- **← Previous window** / **← Previous video** step backward if you
  need to revisit or correct a score.
- **Copy previous scores** copies the previous segment's scores
  forward, useful when posture is unchanged between windows.
- **Back** returns to file selection without losing progress on
  already-scored items.

**⌨️ Keyboard shortcuts** (available once the clip has played through
once):

| Key | Action |
|---|---|
| `0`–`4` | Score the active item with that value (only values up to your chosen point scale apply) |
| `X` | Mark the active item as unscorable |
| `↑` / `↓` | Move the active item up/down (whole-body scoring mode only) |
| `N` | Submit scores and advance to the next window/video |
| `B` | Go back to the previous window |
| `R` | Replay the current segment |
| `C` | Copy the previous segment's scores forward |

In **whole-body scoring mode**, pressing a number or `X` also
automatically advances to the next item, so you can score an entire
segment without touching the mouse. In **region-by-region mode**, each
key applies to the single item currently shown.

When a video is finished, you'll see a "Video completed" confirmation;
once every video in the list is done, a final "Done" summary appears.

### 💾 Output

Depending on what you enabled in Step 1:
- A **CSV file** with all scores, one row per scored window/video.
- An **annotated MP4** per input video, with your scores overlaid,
  saved alongside the original video.

---

## 🛟 3. Troubleshooting

### ❌ "Python was not found" / Microsoft Store popup

Python is not installed, or not on your system PATH. See **Step 1**
above — reinstall from python.org and make sure "Add python.exe to
PATH" is checked. If you use Anaconda/Miniconda, see the **Anaconda /
Miniconda users** section above.

### ❌ "Python 3 was not found" (macOS / Linux)

- **macOS:** install from <https://www.python.org/downloads> (the
  `.pkg` installer). If you're ever prompted to install "Command Line
  Tools", accept that first.
- **Linux:** install via your package manager, e.g.
  `sudo apt install python3 python3-venv python3-pip` on Debian/Ubuntu.

### ❌ `ModuleNotFoundError: No module named 'tkinter'` (Linux only)

`tkinter` ships separately from Python on most Linux distributions:
```
sudo apt install python3-tk        # Debian / Ubuntu
sudo dnf install python3-tkinter   # Fedora
sudo pacman -S tk                  # Arch
```

### ❌ "Failed to create virtual environment" mentioning `ensurepip` (Linux only)

Some Linux distributions split the `venv` module out of the base
Python package. Fix on Debian/Ubuntu:
```
sudo apt install python3-venv
```
then run `./run.sh` again.

### 🔒 Pip / installation fails with a permissions or policy error

Some managed/work computers block package installation via group
policy. If this happens, contact your IT administrator, or run the
tool on a personal machine instead.

### 🆘 Still stuck?

Delete the `.venv` folder and run the setup script again for a clean
reinstall.
