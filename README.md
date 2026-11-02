# GTM Container Ninja

Give every tag, trigger and variable in a Google Tag Manager container a clear, standard name – the same in every brand – without changing what the tracking does.

- **Tags:** `Vendor - Tag type - Action` (e.g. `Meta - cHTML - AddToCart`)
- **Triggers:** `Vendor - Trigger type - Action - Consent` (e.g. `RTB House - WL - Home Page - MKT`)
- **Variables:** `Type - What it holds` (e.g. `DLV - ecommerce.value`)

Full documentation: **[docs/GUIDE.md](docs/GUIDE.md)**

## What it does

- Works out what each item does from its settings and code, then renames it.
- Updates every `{{variable}}` reference and tag-sequencing name, so nothing breaks.
- Uses the same names across brands (brand library).
- Flags duplicates (red), triggers missing a consent check (amber) and names that need a look (blue).
- Optionally deletes unused triggers/variables and sorts items into one folder per vendor.
- Returns an import-ready JSON, an Excel report, a rename map and a rename-in-place script.

## Repository layout

| Path | What it is |
| --- | --- |
| `SKILL.md` | The Claude skill (instructions + embedded script). Save it as a skill in Claude. |
| `scripts/gtm_rename.py` | The renamer (Python 3, `openpyxl` for the Excel report). |
| `scripts/gen_apps_script.py` | Builds a Google Apps Script that renames items in place, so GTM shows them as **Modified**. |
| `web/index.html` | The GTM Container Ninja web page (single file, runs in the browser). |
| `docs/GUIDE.md` | Complete guide: why, features with examples, how to use and test. |
| `examples/` | `vendors.csv`, `naming_rules.json`, `overrides.csv` and a small sample container. |

## Quick start

```bash
pip install openpyxl
python3 scripts/gtm_rename.py examples/sample_container.json --out out --folders --cleanup
# optional shared files:
#   --library brand_library.json --vendors examples/vendors.csv
#   --rules examples/naming_rules.json --overrides examples/overrides.csv
```

Apply the result in GTM so renamed items show as **Modified**:

```bash
python3 scripts/gen_apps_script.py examples/sample_container.json out/sample_container_renamed.json out/rename.gs --folders
```

Then paste `rename.gs` into script.google.com, add the **Tag Manager API** service, set `WORKSPACE_ID`, run with `DRY_RUN = true`, then `false`. See [docs/GUIDE.md](docs/GUIDE.md#8-how-to-use-it).

> GTM's **Import Container** matches items by name, so importing a renamed file shows renamed items as *Deleted + Added*. The rename-in-place script avoids that.

## Use in Claude

Upload `SKILL.md` in a Claude chat and ask Claude to save it as a skill. Then attach a container export and ask, e.g., "Rename this container with GTM Container Ninja, with folders and clean-up."

## Links

- Web page (Claude artifact): https://claude.ai/code/artifact/T4cv7tG4prMip4eTLo42ds
- Guide (Claude doc): https://claude.ai/artifact/HiBQuf1wGyaxS7S1auksr2

## Safety

Only names (and folders, if asked) change: IDs, triggers, settings and code stay the same. Nothing is deleted unless clean-up is on. Test in a new GTM workspace and publish only after sign-off.
