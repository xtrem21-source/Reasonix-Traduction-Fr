"""Resolves every path used by the toolchain — no hard-coded absolute paths.

The repository can be cloned, copied, or moved anywhere: the project root is
derived from this file's location. The only thing taken from the system is
where Reasonix Studio is installed, and even that can be overridden.

Repository layout assumed:

    <repo>/
    ├── scripts/paths.py      # this file
    ├── translations/         # dictionaries, one JSON per language
    ├── sources/              # upstream catalogs, fetched (gitignored)
    └── work/                 # everything generated (gitignored)

Set REASONIX_STUDIO_DIR to point at the installation if it is somewhere unusual.
"""
import os

# --- Project root, derived from this file (so the repo is portable) ---
SCRIPTS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPTS)

# --- Shipped content ---
TRANSLATIONS = os.path.join(ROOT, 'translations')
# The reference (French) dictionary. Other languages live beside it as
# translations/<code>.json.
FR_DICT = os.path.join(TRANSLATIONS, 'fr.json')

# --- Local copies of upstream catalogs (fetched, never redistributed) ---
SOURCES = os.path.join(ROOT, 'sources')

# --- Generated, disposable (gitignored) ---
WORK = os.path.join(ROOT, 'work')
EXTRACTED = os.path.join(WORK, 'extracted')
FR_PARTS = os.path.join(WORK, 'fr_parts')
BACKUP = os.path.join(WORK, 'backup')
TESTDIR = os.path.join(WORK, 'test')
ASAR_ORIG = os.path.join(WORK, 'asar_orig')
ASAR_FR = os.path.join(WORK, 'asar_fr')
APP_FR_ASAR = os.path.join(WORK, 'app_fr.asar')
TOOLS = os.path.join(WORK, 'tools')

# Kept for readability in scripts written against the working tree.
BUILD = WORK

# --- The asar tool ---
# Prefer a copy vendored into work/tools (made by scripts/vendor_asar.py);
# scripts fall back to `npx asar` when it is absent.
ASAR_JS = os.path.join(TOOLS, 'node_modules', 'asar', 'bin', 'asar.js')


def asar_prefix():
    """A shell command prefix that runs asar.

    Prefers the copy vendored into work/tools (made by scripts/vendor_asar.py)
    so the project stays self-contained; falls back to `npx --yes asar`, so a
    fresh clone works as long as Node is installed.
    """
    if os.path.isfile(ASAR_JS):
        return f'node "{ASAR_JS}"'
    return 'npx --yes asar'


# --- The installed Reasonix Studio application (machine-specific) ---
def _localappdata():
    return os.environ.get('LOCALAPPDATA') or os.path.join(
        os.path.expanduser('~'), 'AppData', 'Local')


def app_dir():
    """The Reasonix Studio install directory.

    An explicit REASONIX_STUDIO_DIR wins; otherwise the standard Windows
    location. A path that does not exist is still returned — the caller decides
    whether to stop.
    """
    forced = os.environ.get('REASONIX_STUDIO_DIR')
    if forced:
        return forced
    return os.path.join(_localappdata(), 'Programs', 'Reasonix Studio')


def app_resources():
    return os.path.join(app_dir(), 'resources')


def app_assets():
    """The web interface bundles (frontend-next/dist/assets)."""
    return os.path.join(app_resources(), 'frontend-next', 'dist', 'assets')


def app_asar():
    return os.path.join(app_resources(), 'app.asar')


def app_bin():
    return os.path.join(app_resources(), 'bin')


# --- Reasonix's own user config (holds the optional API key) ---
def reasonix_config_dir():
    appdata = os.environ.get('APPDATA') or os.path.join(
        os.path.expanduser('~'), 'AppData', 'Roaming')
    return os.path.join(appdata, 'reasonix')


def reasonix_env_file():
    return os.path.join(reasonix_config_dir(), '.env')


def require_app():
    """Confirm the application is where we think it is, or explain how to fix it."""
    d = app_dir()
    if not os.path.isdir(d):
        raise SystemExit(
            'Reasonix Studio not found at:\n'
            f'  {d}\n'
            'Set REASONIX_STUDIO_DIR if the application is installed elsewhere.'
        )
    return d
