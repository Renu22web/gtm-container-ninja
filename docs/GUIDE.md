# GTM Container Ninja – Complete Guide

GTM Container Ninja gives every tag, trigger and variable in our Google Tag Manager containers a clear, standard name, the same across every brand, without changing what the tracking does.

## 1. Why we created this skill

Our GTM containers grew over many years. Many people and agencies added tags, each naming them their own way. When we audited the brand containers, we found the same problems again and again:

| Problem | What it looked like |
| --- | --- |
| Names don't say what an item does | "Copy of Trigger test", "OT Marketing - Event", "Custom JS 3" |
| The same thing has different names | One brand: "Facebook Pixel - ATC". Another: "FB Add To Cart" |
| Old items never removed | Triggers and variables that nothing uses any more |
| Hidden copies | The same tag set up twice, so it fires twice and doubles the numbers |
| Consent gaps hard to see | A trigger called "OT Marketing" that doesn't actually check cookie consent |
| Agency names in tag names | "Floodlight - Counter - iCrossing - Blog" |

Fixing this by hand means opening hundreds of items one by one, for every brand. It is slow, easy to get wrong, and the next brand ends up named differently anyway.

We built GTM Container Ninja to do this in minutes, the same way every time, for every brand.

## 2. What it is and how it works

GTM Container Ninja is a Claude skill (and a matching web page). You give it a GTM container export; it gives back the same container with clear names, plus a report.

**It only changes names** (and folders, if you ask). It never changes what a tag sends, when it fires, or any code.

How it works, in 5 steps:

1. **Export** the container from GTM (Admin → Export Container → JSON file).
2. **Give the file** to Claude with the skill, or open it in the web page.
3. **The tool reads every item** and works out what it does from its settings: vendor, event, page, consent.
4. **It renames everything** to the standard format and updates every place a name is used.
5. **You get back** a renamed file, a rename-in-place script, and an Excel report of every change.

## 3. The naming format

Every name is built from parts joined by " - ". Each part answers one question: who is it for, what kind is it, what does it do.

### Tags: Vendor - Tag type - Action

| Part | Meaning | Example |
| --- | --- | --- |
| Vendor | Who the tag sends data to | Meta, GA4, TikTok, Awin |
| Tag type | What kind of tag it is | cHTML (custom code), Event, Template, Image Pixel |
| Action | What it tracks | AddToCart, Purchase, Base |

Examples: `Meta - cHTML - AddToCart` · `GA4 - Event - Add to Cart` · `Google Ads - Template - Conversion - 1072666629`

Tags never carry a consent ending; consent lives on the trigger.

### Triggers: Vendor - Trigger type - Action - Consent

| Part | Meaning | Example |
| --- | --- | --- |
| Vendor | Added only when one vendor's tags use it | RTB House |
| Trigger type | When it fires | PV (page view), CE (custom event), WL (page loaded), CLICK |
| Action | What it is about, taken from the old name | Home Page, ecom_event (add_to_cart) |
| Consent | Added only if it really checks consent | MKT (marketing), ANL (analytics), FUNC (functional) |

Examples: `RTB House - WL - Home Page - MKT` · `PV - All Pages` · `Exclude - PV - Blog` (a trigger used only to block tags)

### Variables: Type - What it holds

Examples: `DLV - ecommerce.value` (data layer value) · `COOKIE - _dyid` · `URL - Path` · `CJS - Marketing Cookies Allowed` (custom JavaScript)

## 4. Core features

### 4.1 Smart naming from settings

**What:** names come from what the item actually does, not just its old label.

**How:** the tool reads the tag's code and settings. It finds the vendor (e.g. `fbq(` in the code = Meta), the event it sends, and the trigger it uses. The old name is only used when the settings say nothing.

**Example:** a GA4 tag sending `add_to_cart` → `GA4 - Event - Add to Cart`.

### 4.2 Old trigger names are respected

**What:** for triggers, the words people already chose are kept and only fitted into the format.

**How:** words like "OT Marketing", "Trigger" and "Event" are removed; the meaningful words stay.

**Example:** `OT Performance - Add to Wishlist` → `Contentsquare - CE - Add to Wishlist - ANL`.

### 4.3 Shared triggers have no vendor

**What:** a trigger used by several vendors' tags doesn't name any one vendor.

**How:** the tool checks which tags use each trigger. One vendor → that vendor goes first. Several vendors → no vendor, and vendor words are removed from the name.

**Example:** `PV - All Pages - for GA4`, used by GA4, Meta and TikTok → `PV - All Pages`.

### 4.4 No repeated words

**Example:** `WL - DY - All pages except PDP - Dynamic Yield` → `Dynamic Yield - WL - All pages except PDP`.

### 4.5 Consent check

**What:** finds triggers that look consent-gated but aren't.

**How:** the consent ending (MKT, ANL, FUNC) is added only if a trigger condition really checks a consent variable. If the old name said "OT Marketing" but no consent check exists, the trigger is highlighted **amber** in the report.

**Example:** `OT - Awin Site Only` with no consent condition → `Awin - WL - Site only`, flagged amber: "add consent condition".

### 4.6 Duplicate finder

**What:** finds items set up exactly the same way.

**How:** if two items would get the same name, the copy is numbered (2), (3) and highlighted **red**, with a note naming the one to keep.

**Example:** `Meta - cHTML - AddToCart (2)` → "Duplicate of Meta - cHTML - AddToCart – re-point, then delete".

### 4.7 Clean-up of unused items (optional)

**What:** removes triggers and variables that nothing uses.

**How:** a trigger is kept if any tag uses it (paused tags count) or if a trigger group that is in use contains it. A variable is kept if anything in use refers to it, even through other variables. Tags are never deleted. Every removed item is listed in a **grey** sheet.

**Example:** a trigger that only sits inside the unused group "Copy of Trigger test" → the group and the trigger are both removed. A trigger in that group **and** in a used group stays.

### 4.8 One folder per vendor (optional)

| Folder | What goes in |
| --- | --- |
| Vendor name (Meta, GA4…) | That vendor's tags, and triggers/variables only they use |
| 00 Consent & CMP | Consent tags and consent variables |
| 01 Shared - Multiple Vendors | Triggers/variables used by two or more vendors |
| 02 No Vendor - Helpers | Items with no vendor |

### 4.9 Links never break

**What:** when a variable is renamed, every tag, trigger and variable that uses it is updated too.

**Example:** `{{Custom JS - Marketing Cookies Allowed}}` inside 40 tags becomes `{{CJS - Marketing Cookies Allowed}}` in all 40.

### 4.10 Import check

**What:** makes sure GTM will accept the file. It fixes known import errors (such as hidden fields in old Gallery templates) and lists anything a person must check, like a tag pointing to a missing trigger.

### 4.11 Safe to run again

Running it on an already-renamed container changes nothing that's already correct. Only new or non-standard items are renamed, so you can re-run whenever new tags are added.

### 4.12 Rename in place (shows "Modified" in GTM)

**What:** a Google Apps Script that applies the renames directly in a GTM workspace through the Tag Manager API.

**Why:** GTM's Import matches items by **name**, so an imported renamed file shows renamed items as Deleted + Added. Renaming in place keeps each item and shows it as **Modified**; unused items show as **Deleted**.

**How:** `scripts/gen_apps_script.py` builds the script from the original export and the renamed file. See section 8.

## 5. Standardising across brands

### 5.1 Brand library

**What:** a shared list of agreed names. The same set-up gets the same name in every brand.

**How:**

1. Rename the brand with the fullest set-up first and approve its names. This becomes the library (`brand_library.json`).
2. Run the next brand with the library. Any item set up the same way gets exactly the library's name. "Same way" is judged from settings (event, code, conditions), so it works even when old names differ.
3. Items the library hasn't seen are named by the normal rules.
4. Each run adds the brand's new items to the library, so the next brand benefits.

**Example:** Dermstore has `Meta - cHTML - AddToCart`. Brand B calls the same tag "FB ATC new". With the library, Brand B's tag becomes `Meta - cHTML - AddToCart` too. In our test, 574 of 607 Brand B names matched Dermstore automatically.

### 5.2 New vendors

Add them once to `vendors.csv`: the vendor name plus words that identify it in tag names or code. Without the list, the first part of the old name is used as the vendor.

**Example:** `Power Reviews` = "powerreviews, ui.powerreviews.com". A tag "Reviews widget - PDP" whose code loads ui.powerreviews.com → `Power Reviews - cHTML - Reviews widget - PDP`.

### 5.3 Team rules (`naming_rules.json`)

| Setting | Default | Example change |
| --- | --- | --- |
| Tag type labels | cHTML, Image Pixel, Template | Use "HTML" instead of "cHTML" |
| Words never kept | iCrossing | Add another agency name |
| Folder names | 00 Consent & CMP, 01 Shared…, 02 No Vendor… | Rename a folder |

### 5.4 Fix list (names you choose)

Add the item to the Fix list (search, the + button, or drag a row), type the new name, then export the list. The skill reads it as an overrides file: `Item, Old name, New name`. Names you set always win over the library and the rules.

## 6. The web page

The same rules run in a web page (`web/index.html`). The file stays in your browser; nothing is uploaded.

| Feature | What it does |
| --- | --- |
| Table with Folder column | Old name, new name, vendor, folder for every item |
| Details | Click a name to see conditions, variables, which tags use it |
| Select & export | Tick items like in GTM and export only those, with everything they need |
| Find & replace | Change a word in many names at once |
| History | Undo / redo every name change |
| Name score | Share of names in the format, before and after |
| Compare brands | Load other brands' exports and see what differs |
| Test after import | A test plan for each journey step |
| Brand library | Save this brand's names; reuse them for the next |

**Partial export:** import with **Merge → Overwrite conflicting**. Never use Overwrite for a partial file; it deletes everything not in the file.

**Team sharing:** when opened as the Claude artifact, settings and the brand library can be shared with the team. Opened as a plain HTML file, everything stays in that browser.

## 7. What you get back

| File | What it is for |
| --- | --- |
| Excel summary (.xlsx) | Every old and new name, folder, vendor and action, colour-coded |
| Renamed container (.json) | Import into a GTM test workspace |
| Rename-in-place script (.gs) | Apply the renames in a GTM workspace so they show as Modified |
| Rename map (.csv) | The same changes as a plain list |
| Brand library (.json) | Agreed names to use for the next brand |

| Colour | Meaning | What to do |
| --- | --- | --- |
| Red | Duplicate of another item | Point anything using it to the original, then delete |
| Amber | Named as consent-gated but has no consent check | Add the consent condition |
| Blue | Named from the old name only | Quick check that the name is right |
| Grey | Removed as unused (clean-up only) | Check the list before importing |

## 8. How to use it

### Rename a container

1. In GTM: **Admin → Export Container**, choose the workspace, download the JSON file.
2. In Claude: attach the file and ask, for example, "Rename this container with GTM Container Ninja, use folders and clean up unused items."
3. Also attach any shared files: `brand_library.json`, `vendors.csv`, `naming_rules.json`, and the brand's overrides file.
4. Review the Excel report: red, amber and blue rows first.
5. Not happy with a name? Add it to the overrides / Fix list and run again.
6. Keep the new `brand_library.json` for the next brand.

Command line:

```bash
python3 scripts/gtm_rename.py GTM-XXXX_workspace12.json --out out --folders --cleanup \
  --library brand_library.json --vendors examples/vendors.csv --rules examples/naming_rules.json
```

### Apply the changes so they show as "Modified" (recommended)

1. Build the script: `python3 scripts/gen_apps_script.py GTM-XXXX_workspace12.json out/GTM-XXXX_workspace12_renamed.json rename.gs --folders`
2. In GTM, create a **new workspace**; note the number after `/workspaces/` in the address bar.
3. script.google.com → New project → paste `rename.gs` → set `WORKSPACE_ID` → Services → add **Tag Manager API**.
4. Run `run` with `DRY_RUN = true` and read the log. Then set `DRY_RUN = false` and run again; repeat if it says "Time limit reached" until "ALL DONE".
5. Renamed items show as **Modified**, unused ones as **Deleted**. Nothing is published.

### Or import the renamed file

GTM → Admin → **Import Container** → renamed file → **New workspace** + **Overwrite**. Renamed items appear as **Deleted + Added**, because Import matches by name. The end result is the same.

### Test safely

1. Use **Preview** to walk the journey: home, category, product, add to cart, basket, checkout, purchase. The same tags must fire as before.
2. Publish only after sign-off. GTM keeps the previous version for rollback.

## 9. Benefits, safety and FAQ

**Benefits:** faster work, fewer mistakes, cleaner data (duplicates found), consent gaps visible, one standard across brands, easy audits and handovers.

**Safety:** only names (and folders, if asked) change. Nothing is deleted unless clean-up is on, and every removed item is listed. Duplicates and consent gaps are only reported. Everything is tested in a separate workspace first.

- **Will our reports or data change?** No. Tags send the same data; only labels change.
- **Server-side containers?** Yes, browser and server containers.
- **New tags later?** Run it again. Only new or non-standard items change.
- **Different name wanted?** Use the Fix list / overrides. It sticks on every run.
- **Unknown vendor?** Add it to `vendors.csv`, or the first part of the old name is used.

## 10. Glossary of short codes

| Code | Means |
| --- | --- |
| cHTML | Custom HTML tag (custom code) |
| Template | Tag or variable built from a GTM template |
| PV / DOM / WL | Page view / DOM ready / window loaded trigger |
| CE | Custom event trigger |
| CLICK / LINK | Click / link click trigger |
| VIS | Element visibility trigger |
| TG | Trigger group |
| Exclude | Trigger used only to block tags |
| MKT / ANL / FUNC | Waits for marketing / analytics / functional cookie consent |
| DLV | Data layer variable |
| CJS | Custom JavaScript variable |
| TPL | Template variable |
| CONST | Constant variable |
| COOKIE | First-party cookie variable |
| URL | URL variable |
| LT / RT | Lookup table / RegEx table variable |
| JSV | JavaScript variable |
