# First Use

For the current public-facing install and first-run workflow, use:

- `README.md` — installation + everyday command surface;
- `docs/ZERO_TO_GROK.md` — complete copy/paste path from install to Controller/worker/trace;
- `docs/SELECTION_REFERENCE.md` — roles, profiles, lenses, claims, project classes, and result states.

## Short path

Pip from GitHub:

```bash
python3 -m pip install "git+https://github.com/mldugom/ooda.git"
ooda setup
```

Or from a clone:

```bash
git clone https://github.com/mldugom/ooda.git
cd ooda
bash install.sh
```

Adopt an existing repo:

```bash
cd ~/repos/example-app
ooda init --project-id example-app --project-class software-product
ooda doctor
grok-safe
```

Then in Grok:

```text
/ooda-controller Jump into this repo. Use only the minimum durable state needed to orient. What deserves attention next? If deeper evidence is needed, propose the smallest worker mission.
```

The point of first use is to start working, not to complete an adoption ceremony.
