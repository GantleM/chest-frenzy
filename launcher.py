import FreeSimpleGUI as sg
import subprocess
import threading
import requests
import zipfile
import shutil
import sys
import os
import io

from assets import local_version as local_version
# -------------------------------------------
#  CONFIG 
# -------------------------------------------
GAME_FILE       = "chest_frenzy.py"          # entry-point to launch
CURRENT_VERSION = local_version.get_local_version()           

# Version-check endpoint  (returns JSON: {"version": "x.xx"})
VERSION_URL      = "https://GantleM.pythonanywhere.com/version"

# ZIP of the whole repo (GitHub "Download ZIP" URL, or your own server)
# e.g. GitHub:  https://github.com/<user>/<repo>/archive/refs/heads/main.zip
DOWNLOAD_URL     = "https://github.com/GantleM/chest-frenzy/archive/refs/heads/main.zip"

# Top-level folder name inside the ZIP  (GitHub adds "<repo>-<branch>")
ZIP_ROOT_FOLDER  = "chest-frenzy-main"

# Folders / files that must NEVER be touched during an update
PROTECTED        = {"saves", "launcher.py"}
# -------------------------------------------


def check_for_update():
    """
    Returns (latest_version: str, has_update: bool) or (None, False) on failure.
    """
    try:
        r = requests.get(VERSION_URL, timeout=5)
        data = r.json()
        latest = str(data.get("version", "")).strip()
        if latest:
            return latest, latest != CURRENT_VERSION
    except Exception:
        pass
    return None, False


def download_and_install(latest_version, progress_cb, status_cb):
    """
    Downloads the ZIP, extracts it, and replaces game files while
    leaving PROTECTED paths alone.

    progress_cb(int 0-100)  - called to update a progress bar
    status_cb(str)          - called to update a status label
    """
    try:
        # ── 1. Download ──────────────────────────────────────────────
        status_cb("Downloading update…")
        r = requests.get(DOWNLOAD_URL, stream=True, timeout=30)
        r.raise_for_status()

        total = int(r.headers.get("content-length", 0))
        downloaded = 0
        buf = io.BytesIO()
        for chunk in r.iter_content(chunk_size=65536):
            buf.write(chunk)
            downloaded += len(chunk)
            if total:
                progress_cb(int(downloaded / total * 60))   # 0-60 %

        # ── 2. Extract to a temp folder ───────────────────────────────
        status_cb("Extracting files…")
        progress_cb(65)
        buf.seek(0)
        tmp_dir = "_update_tmp"
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        os.makedirs(tmp_dir)

        with zipfile.ZipFile(buf) as zf:
            zf.extractall(tmp_dir)

        # ── 3. Locate extracted root ──────────────────────────────────
        extracted_root = os.path.join(tmp_dir, ZIP_ROOT_FOLDER)
        if not os.path.isdir(extracted_root):
            # Fall back: first subdirectory inside tmp_dir
            subdirs = [d for d in os.listdir(tmp_dir)
                       if os.path.isdir(os.path.join(tmp_dir, d))]
            if subdirs:
                extracted_root = os.path.join(tmp_dir, subdirs[0])
            else:
                extracted_root = tmp_dir

        # ── 4. Copy new files over, skip protected paths ──────────────
        status_cb("Installing update…")
        progress_cb(75)
        game_dir = os.path.abspath(".")

        for item in os.listdir(extracted_root):
            if item in PROTECTED:
                continue                            # never touch saves / launcher

            src  = os.path.join(extracted_root, item)
            dest = os.path.join(game_dir, item)

            if os.path.isdir(src):
                if os.path.exists(dest):
                    shutil.rmtree(dest)
                shutil.copytree(src, dest)
            else:
                shutil.copy2(src, dest)

        progress_cb(95)

        # ── 5. Clean up temp folder ───────────────────────────────────
        shutil.rmtree(tmp_dir, ignore_errors=True)
        status_cb(f"Updated to v{latest_version}!")
        progress_cb(100)
        return True

    except Exception as e:
        status_cb(f"Update failed: {e}")
        shutil.rmtree("_update_tmp", ignore_errors=True)
        return False


def launch_game():
    """Starts the main game as a separate process and closes the launcher."""
    python = sys.executable
    subprocess.Popen([python, GAME_FILE], cwd=os.path.abspath("."))
    window.write_event_value("-QUIT-", None)


# ─────────────────────────────────────────────
#  GUI
# ─────────────────────────────────────────────
sg.theme("DarkBlue")

layout = [
    [sg.VPush()],
    [sg.Push(),
     sg.Text("CHEST FRENZY", font=("Arial Bold", 22), justification="center"),
     sg.Push()],
    [sg.Push(),
     sg.Text(f"v{CURRENT_VERSION}", font=("Arial", 10), key="-VERSION LABEL-",
             text_color="gray"),
     sg.Push()],
    [sg.VPush()],

    # Update banner – hidden until we know there's an update
    [sg.Push(),
     sg.Text("", key="-UPDATE TEXT-", font=("Arial", 11),
             text_color="yellow", visible=False),
     sg.Push()],

    # Buttons row
    [sg.Push(),
     sg.Button("▶  Play", key="-PLAY-", size=(14, 2),
                font=("Arial Bold", 13), button_color=("white", "#1a6e1a")),
     sg.Button("⬆  Update", key="-UPDATE-", size=(14, 2),
                font=("Arial Bold", 13), button_color=("white", "#1a4a8e"),
                visible=False),
     sg.Push()],

    [sg.VPush()],

    # Progress / status (shown during update)
    [sg.Push(),
     sg.ProgressBar(100, orientation="h", size=(35, 18), key="-PROGRESS-",
                    visible=False, bar_color=("#4a9eff", "#1a1a2e")),
     sg.Push()],
    [sg.Push(),
     sg.Text("", key="-STATUS-", font=("Arial", 10), text_color="light gray"),
     sg.Push()],

    [sg.VPush()],
    [sg.Push(),
     sg.Text("Checking for updates…", key="-ONLINE STATUS-",
             font=("Arial", 9), text_color="gray"),
     sg.Push()],
]

window = sg.Window(
    "Chest Frenzy Launcher",
    layout,
    size=(420, 340),
    finalize=True,
    element_justification="center",
)

# ── Background update-check ───────────────────
_latest_version = None

def _bg_check():
    global _latest_version
    latest, has_update = check_for_update()
    _latest_version = latest
    if latest is None:
        window.write_event_value("-CHECK DONE-", "offline")
    elif has_update:
        window.write_event_value("-CHECK DONE-", f"update:{latest}")
    else:
        window.write_event_value("-CHECK DONE-", "up_to_date")

threading.Thread(target=_bg_check, daemon=True).start()


# ── Event loop ────────────────────────────────
_updating = False

while True:
    event, values = window.read(timeout=100)

    if event in (sg.WIN_CLOSED, "Exit", "-QUIT-"):
        break

    # ── Version-check result arrives ──────────
    if event == "-CHECK DONE-":
        msg = values["-CHECK DONE-"]

        if msg == "offline":
            window["-ONLINE STATUS-"].update("● Offline – no update check", text_color="gray")

        elif msg == "up_to_date":
            window["-ONLINE STATUS-"].update("● Online – game is up to date ✓", text_color="#4caf50")

        elif msg.startswith("update:"):
            new_ver = msg.split(":", 1)[1]
            window["-ONLINE STATUS-"].update("● Online", text_color="#4caf50")
            window["-UPDATE TEXT-"].update(
                f"Update available!  v{CURRENT_VERSION}  →  v{new_ver}", visible=True)
            window["-UPDATE-"].update(visible=True)

    # ── Play ──────────────────────────────────
    if event == "-PLAY-" and not _updating:
        if not os.path.isfile(GAME_FILE):
            sg.popup_error(f"Could not find '{GAME_FILE}'.\n"
                           "Make sure the launcher is in the game folder.",
                           title="File not found")
        else:
            window["-PLAY-"].update(disabled=True)
            threading.Thread(target=launch_game, daemon=True).start()

    # ── Update ────────────────────────────────
    if event == "-UPDATE-" and not _updating:

        confirm = sg.popup_yes_no(
            f"Download and install v{_latest_version}?\n\n"
            "Your save files will NOT be touched.",
            title="Confirm Update")

        if confirm == "Yes":
            _updating = True
            window["-UPDATE-"].update(disabled=True)
            window["-PLAY-"].update(disabled=True)
            window["-PROGRESS-"].update(visible=True)
            window["-STATUS-"].update("Starting download…")

            def _do_update():
                ok = download_and_install(
                    _latest_version,
                    lambda p: window.write_event_value("-PROGRESS UPDATE-", p),
                    lambda s: window.write_event_value("-STATUS UPDATE-",   s),
                )
                window.write_event_value("-UPDATE DONE-", ok)

            threading.Thread(target=_do_update, daemon=True).start()

    if event == "-PROGRESS UPDATE-":
        window["-PROGRESS-"].update(values["-PROGRESS UPDATE-"])

    if event == "-STATUS UPDATE-":
        window["-STATUS-"].update(values["-STATUS UPDATE-"])

    if event == "-UPDATE DONE-":
        _updating = False
        success = values["-UPDATE DONE-"]
        window["-PLAY-"].update(disabled=False)
        if success:
            window["-UPDATE TEXT-"].update(
                f"✓ Game updated to v{_latest_version}!", visible=True)
            window["-UPDATE-"].update(visible=False)
            window["-VERSION LABEL-"].update(f"v{_latest_version}")
        else:
            window["-UPDATE-"].update(disabled=False)
            sg.popup_error("Update failed – check your internet connection\n"
                           "and try again.", title="Update Error")

window.close()
