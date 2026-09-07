# Public install

OODA supports two lightweight installation paths.

## Option A — clone the repository

Best when you want the full OODA experience, including Grok skills.

```bash
mkdir -p ~/repos
cd ~/repos
git clone https://github.com/mldugom/ooda.git
cd ooda
bash install.sh
```

This installs:

- `ooda` CLI;
- `grok-safe` launcher;
- Grok `/ooda` worker skill;
- Grok `/ooda-controller` control skill.

The installer uses symlinks back to the cloned repository so `git pull` updates the installed OODA/Grok behavior.

## Option B — pip directly from GitHub

Best when you mainly want the CLI and bounded Grok launcher without maintaining an OODA checkout.

```bash
python3 -m pip install --user git+https://github.com/mldugom/ooda.git
```

This installs console commands:

```text
ooda
grok-safe
```

The pip package does not currently install Grok slash-command skills into `~/.grok/skills`. Use the clone + `bash install.sh` route when you want `/ooda` and `/ooda-controller` as well.

PyPI publication is deliberately deferred until public usage justifies a release process. Pip-from-GitHub is the supported lightweight package path for now.

## Grok requirement

`grok-safe` expects the Grok CLI binary at:

```text
~/.grok/bin/grok
```

If Grok is installed somewhere else:

```bash
GROK_BIN=/path/to/grok grok-safe
```

The launcher applies OODA's public bounded-execution policy, defaults to six turns, and disables subagents. Override the turn limit only when justified:

```bash
GROK_SAFE_MAX_TURNS=10 grok-safe
```

## Verify

```bash
ooda help
grok-safe --help
```

Then, from an OODA-adopted project:

```bash
grok-safe
```

and inside Grok:

```text
/ooda-controller <your question>
```

when the clone installation was used.

## Existing repo adoption

```bash
cd ~/repos/<project>
ooda init --project-id <project> --project-class software-product
ooda doctor
```

Use `--scaffold` only for a genuinely new/minimal repo. Existing repos with useful docs should normally receive only the thin `.ooda/` overlay.
