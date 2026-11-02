---
name: gtm-container-ninja
description: GTM Container Ninja - rename every tag, trigger and variable in a GTM container export to the PLC naming convention, give the same set-up the same name across all brands (brand library), optionally clean up unused items, and return an Excel summary, rename map and import-ready JSON.
---

# GTM Container Ninja

Takes a Google Tag Manager container export, works out what each tag, trigger and variable actually does from its configuration (tag type, template, pixel code, event names, trigger conditions, dataLayer keys), renames it so the name says what it is, and returns a file that can be imported into GTM to test. Behaviour never changes: only names (and, optionally, folders) change.

## When to use

The user shares a GTM container export (`GTM-XXXX_workspaceNN.json`, browser or server) and asks to standardise, review or fix naming, clean up unused items, or make several brands' containers use the same names. Also when they ask what the naming convention is.

## Brand files to keep (ask for them, reuse them on every run)

| File | What it holds | Scope | Flag |
| --- | --- | --- | --- |
| `brand_library.json` | the agreed name for every set-up already named in a brand | **all brands** | `--library` |
| `vendors.csv` | vendors the tool does not know (`Vendor,Match`) | all brands | `--vendors` |
| `naming_rules.json` | team rules: tag type labels, words never kept, folder names | all brands | `--rules` |
| `<brand>_overrides.csv` | names set by hand for one brand (`Item,Old name,New name`) | one brand | `--overrides` |

The page exports the same files (Brand library, My vendors, Team rules, Fix list → "Export my names"), and the skill writes `<name>_library.json` after every run. Ask the user for the latest `brand_library.json`, `vendors.csv` and `naming_rules.json` before renaming a new brand.

## Steps

1. **Find the export.** Use the attached file, or ask for it: GTM → Admin → Export Container → choose the workspace/version → download JSON. Confirm it has `containerVersion` with `tag` / `trigger` / `variable`.
2. **Write the script** at the end of this skill to `gtm_rename.py` in the working (scratch) directory, exactly as given. If the user has a brand overrides file (e.g. `dermstore_overrides.csv`, or the "Export my names" file from the page's Fix list), add `--overrides <file>` to every run. If the user has vendors the tool does not know, write `vendors.csv` (`Vendor,Match` – the name to use, then comma-separated words that identify it in tag names, template names or code, e.g. `Power Reviews,"powerreviews, ui.powerreviews.com"`; the page's "My vendors" export is this file) and add `--vendors vendors.csv`.
3. **Run it:** `python3 gtm_rename.py <export.json> --out <outdir> --library brand_library.json`; add `--folders` if the user wants one folder per vendor (see *Folders* below); add `--cleanup` when the user wants triggers and variables that nothing uses deleted (see *Clean-up* below); add `--vendors`, `--rules`, `--overrides` when the user has those files. Leave `--library` out only for the very first brand.
4. **Web page alternative.** The same rules run in the "GTM Container Ninja" artifact page (browser only, file not uploaded); point users there when they prefer a page to the chat. The page adds:
   - **Fix list** – collect the items the user is not happy with (search box, the + button on a row, or drag a row in), type the wanted name and an optional note; every reference follows. "Export my names" downloads the overrides file (`Item,Old name,New name,Note`) for `--overrides`; "Import names" loads one (also an existing brand overrides file). The list and names are remembered per container in that browser.
   - **My vendors** – the vendor list above (export/import as `vendors.csv`), remembered in that browser.
   - **Folder column** – the folder each item will be in after import (and, with the folders option off, the folder it would get).
   - **Brand library** – "Save this brand's names to the library" after a brand is done; every next brand reuses those names. Export/import as `brand_library.json` (same file as `--library`).
   - **Team rules** – the rule editor (tag type labels, words never kept, folder names); export/import as `naming_rules.json` (`--rules`).
   - **Shared with the team** – vendors, team rules, the brand library and each container's names are stored on the page for everyone who opens it (badge "Shared with your team"); without that, only in that browser.
   - **Details** – click an old name: what the item does (triggers and their conditions, exceptions, variables used, which tags use it, trigger groups, paused/consent status), with links between items.
   - **Select & export** – tick items (or "select all shown") and export only those, with the triggers, variables and templates they need. A partial file is imported with **Merge → Overwrite conflicting tags, triggers and variables**, never with Overwrite (that would delete everything not in the file).
   - **Find & replace**, **History** (undo/redo of every name change), **Name score** (share of names in the format, before/after, minus duplicates and missing consent), **Compare brands** (load other exports: vendors and tag actions per brand, what differs, CSV) and **Test after import** (journey test plan per step – home, category, product, add to cart, basket, checkout, purchase – as JSON/CSV for the GTM journey-tester skill).
5. **Review before handing over.** Open `<name>_summary.xlsx` (sheets: Summary, Rename Map, Duplicates – delete, No consent condition, Deleted – not used (with `--cleanup`), Import check) and check:
   - **Import check sheet:** every run also makes the file safe to import. *Fixed* rows are problems GTM would refuse that the script repaired (today: hidden fields in old Gallery templates such as Snap Pixel, which cause "Hidden parameters are not allowed"; a template that had to be edited also loses its Gallery link, because GTM rejects a changed Gallery template with "This field is invalid (or unsupported)" on `galleryReference` – it imports as a custom template). *Check* rows need a person: a tag pointing to a trigger that is missing, a `{{variable}}` that does not exist in the container, or two items with the same name. If a *Fixed* row says the template code reads the removed field, update that template from the Gallery before publishing. A template with no code (GTM error "template_data: Missing section ___INFO___") cannot be repaired from the file – export the container again from GTM so the template code is included.
   - **red rows – duplicates:** two items would get the same name because they have the same set-up. The copy is numbered `(2)`, `(3)`… and its Action says "Delete (duplicate) – re-point first"; the note names the original to keep. **Same name, different set-up is never a duplicate:** when two items end up with the same name but are set up differently (e.g. old names `cjs - AI Shopping Assistant Experiment Present` and `cjs -AI Shopping Assistant Experiment Present` with different code), a word only one of them uses is added – a variable its code reads, else a property it reads: `CJS - AI Shopping Assistant Experiment Present - fuel_coach_experiment_wave_01`, `CJS - Product Page Product ID - ProdId from URL`. If nothing tells them apart, the copy is numbered with the note "NAME CLASH … different set-up, keep both and check the name" (Action "Check name", never "Delete"). **Paused tags are never deleted or flagged:** when a paused item has the same set-up as a live one, the **live** item keeps the clean name and the paused one gets the same formatted name with ` - Paused` (`Criteo - cHTML - addToCart - Paused`; for a trigger before the consent ending: `Criteo - CE - Add to cart - Paused - MKT`), note "PAUSED copy of live …", Action "Rename"; a trigger or variable used only by paused tags counts as paused (`DLV - ecommerce.items - Paused`), so a live item never gets the `(2)`. Live copies with the same code and the same firing conditions are only numbered – the trigger's name is never added to a tag name to tell them apart, and trigger words an earlier run added to tag names are removed on a re-run.
   - **amber rows – no consent condition:** triggers whose old name implied a consent gate ("OT Marketing …", "OT Performance …", "OT - …") but whose conditions test no consent variable. They are renamed to the standard format like every other trigger – no "OT", no "Marketing", no consent ending – and the Action says to add the consent condition later (roadmap Phase 4).
   - **grey rows – deleted, not used** (only with `--cleanup`): triggers and variables removed because nothing in use depends on them. Check the list before importing.
   - **blue rows – named from the old name only** (no config signal): make sure the name still says what the item does.
   - consent variables are **only renamed, never swapped**: a template consent variable becomes `TPL - <name>` (e.g. `TPL - Marketing Cookies Allowed`) and a Custom JS one becomes `CJS - <name>` (e.g. `CJS - Marketing Cookies Allowed`). Both stay; references keep pointing at the same variable as before.
   - a file that was **already renamed** can be run again (for example the `_renamed.json` itself, or after more tags were added): names already in the standard format are kept, so only new or non-standard items change.
   If a name is wrong, write `overrides.csv` (`Item,Old name,New name`) and re-run with `--overrides overrides.csv`. Repeat until the map is clean.
6. **Deliver** (send files, don't paste them):
   - `<name>_summary.xlsx` – the summary sheet with the colour key, plus the full rename map with red / amber / blue highlighting and an Action column,
   - `<name>_renamed.json` – import-ready container,
   - `<name>_rename_map.csv` and `<name>_summary.md` – plain-text copies of the same (the map and every Excel sheet have a **Folder** column: the folder after import – the vendor folder with `--folders`, otherwise the item's current folder or "Unfiled"),
   - `<name>_library.json` – the brand library with this brand added; tell the user to keep it as `brand_library.json` and use it for the next brand,
   - in the reply: counts per item type, references updated, number of duplicates (red), no-consent triggers (amber) and deleted unused items (grey), what the import check fixed or flagged, then the top items to check.
7. **Tell them how to test** (below).

## Naming convention

Every name says what kind of item it is and what it does. Separator is always ` - `. Vendor names are fixed: Meta (not Facebook), TikTok, Awin, Contentsquare, Floodlight, CHEQ, Microsoft Ads, X (not Twitter), RTB House, Dynamic Yield, TTD, Xandr. Consent endings `MKT` (marketing), `ANL` (analytics), `FUNC` (functional) are used on **triggers only, never on tags**.

### Tags – `Vendor - Tag type - Action`

- **Vendor** first, then the **tag type**, then the **action** (what the tag does). No consent ending on a tag – the consent lives in its trigger.
- **Tag types:** `cHTML` (Custom HTML – never "HTML"), `Image Pixel`, `Template` (custom templates and the Google Ads conversion tag), `Event` (GA4), `Google Tag`, `Remarketing`, `Conversion Linker`, `Counter` / `Sales` (Floodlight), `UET`, `OneTag`, `Pixel` (Pinterest).
- **Action** comes from the tag itself first (GA4 event name, the pixel's track call, Criteo's event, the Listrak call, the Google Ads conversion ID), the old name only as a fallback.
- **GA4 actions are written in words:** first letter of each word capital, no underscores, small words (to, and, of, for…) lower case: `add_to_cart` → `GA4 - Event - Add to Cart`. Never "Events", "errors", "ecom_event", "elysiumEvent" or an event name in brackets. A generic `errors` event is named from its `type` parameter (`GA4 - Event - Page Not Found`).
- **No vendor found:** never "Utility" – the first part of the old name is the vendor and `cHTML` goes after it: `Hearst - Add To Cart` → `Hearst - cHTML - Add To Cart`; a one-part name becomes `<name> - cHTML` (`Humankind - cHTML`).
- **Agency names** (iCrossing) are never kept: `Floodlight - Counter - iCrossing - Blog` → `Floodlight - Counter - Blog`.

| Variation | Format | Example |
| --- | --- | --- |
| GA4 event | `GA4 - Event - <Event In Words>` | `GA4 - Event - Add to Cart`, `GA4 - Event - View Item List` |
| GA4 event sent from a variable | `GA4 - Event - <group>` | `GA4 - Event - Ecommerce Events` |
| GA4 configuration | `GA4 - Google Tag - Configuration` | `GA4 - Google Tag - Configuration` |
| Google Ads conversion (built-in tag) | `Google Ads - Template - Conversion - <conversion ID>` | `Google Ads - Template - Conversion - 1072666629` |
| Google Ads conversion (Custom HTML) | `Google Ads - cHTML - Conversion - <conversion ID>` | `Google Ads - cHTML - Conversion - 1009160399` |
| Google Ads remarketing | `Google Ads - Remarketing - <page / event>` · `Google Ads - cHTML - Remarketing - <what>` | `Google Ads - Remarketing - View Item`, `Google Ads - cHTML - Remarketing - All Pages - SEM` |
| Google Ads linker | `Google Ads - Conversion Linker` | `Google Ads - Conversion Linker` |
| Floodlight | `Floodlight - Counter - <activity>` · `Floodlight - Sales - <activity>` | `Floodlight - Counter - Blog` |
| Pixel base / set-up tag | `<Vendor> - cHTML - Base` | `TikTok - cHTML - Base` |
| Pixel event | `<Vendor> - cHTML / Template - <VendorEventName>` | `Meta - cHTML - AddToCart`, `TikTok - cHTML - Conversion` |
| Criteo | `Criteo - cHTML - <Criteo event>` (`viewPage` = All pages, `trackTransaction` = trackTransaction (Conversion)) | `Criteo - cHTML - viewBasket`, `Criteo - cHTML - trackTransaction (Conversion)` |
| Contentsquare | `Contentsquare - cHTML - <action from the old name>` – the `_uxa` command (trackPageview, setPIISelectors, trackDynamicVariable, ec, setOption) is never used as the action | `Content Square - Add to Cart Popup Dismissed` → `Contentsquare - cHTML - Add to Cart Popup Dismissed`, `Content Square App Base tag` → `Contentsquare - cHTML - App Base tag` |
| Listrak | `Listrak - cHTML - <action>` | `Listrak - cHTML - Product Browse`, `Listrak - cHTML - Email Capture` |
| Image pixel | `<Vendor> - Image Pixel - <What>` | `Awin - Image Pixel - Conversion` |
| Awin | `Awin - Template - MasterTag` · `Awin - Template - Consent Signals` · `Awin - cHTML - Conversion` | `Awin - cHTML - Conversion` |
| Consent | `Consent - <Tag type> - <what>` | `Consent - Template - Consent Mode - Default` |
| No vendor found | `<first part of old name> - cHTML - <rest>` | `Hearst - cHTML - Add To Cart`, `Narrativ - cHTML - All Pages` |
| Duplicate set-up | numbered `(2)`, highlighted red | `Meta - cHTML - AddToCart (2)` → delete after re-pointing |

**Brand-specific actions** that cannot be read from the code (for example which Listrak `Signup.SetValue` tag is Email and which is SMS, or `Dynamic Yield - cHTML - View Item` for a context-update tag) go in that brand's `overrides.csv` (`Item,Old name,New name`). The *Old name* can be the tag's current name **or** the standard name the script would give it, so one overrides file keeps working when the export is renamed again. Keep one overrides file per brand and re-use it on every run.

### Triggers – `Vendor - Trigger type - Action - Consent`

| Code | Trigger type | Example |
| --- | --- | --- |
| CE | Custom Event | `CE - purchase`, `Meta - CE - ecom_event (add_to_cart) - MKT` |
| PV | Page View | `PV - All Pages`, `Awin - PV - Checkout Complete - Site Only` |
| DOM / WL | DOM Ready / Window Loaded | `RTB House - WL - Home Page - MKT` |
| CLICK / LINK | All Elements / Just Links click | `Listrak - CLICK - Contact Preferences case - MKT` |
| VIS | Element Visibility | `VIS - RingCentral_Icon_Viewed` |
| FORM, HIST, TIMER, SCROLL, YT, JSERR | other auto-event types | `SCROLL - 50` |
| TG | Trigger Group | `TG - No marketing consent then consent` |
| written in full | Initialization / Consent Initialization | `Dynamic Yield - Initialization - All Pages`, `Consent Initialization - All Pages` |
| Exclude | used only as an exception (blocking) trigger | `Exclude - PV - Blog`, `Exclude - CE - Listrak - Merchant ID no` |

- **Vendor** first when every tag that uses the trigger (directly or through a trigger group) belongs to one vendor – also vendors not in the built-in list (`Hearst`, `Narrativ`, `Spotx and Hulu`…). Google (GA4, Google Ads, Floodlight), consent and no-vendor triggers have no vendor part. If the action would be only the vendor's name, the vendor part is left out (`VIS - RingCentral_Icon_Viewed`, not `RingCentral - VIS - RingCentral`).
- **Action comes from the old name first.** The old name's own words are kept and only fitted into the format: prefixes such as "OT Performance", "OT Marketing", "CE", "Event" and "Trigger" are removed, nothing else is reworded (`OT Performance - Add to Wishlist` → `Contentsquare - CE - Add to Wishlist - ANL`; `OT Performance - Event - ATC Modal closed` → `Contentsquare - CE - ATC Modal closed - ANL`; `OT Marketing - RTB House Product Page Trigger` → `RTB House - CE - Product Page - MKT`). Raw event names in the old name stay as written (`ecom_event (add_to_cart)`, `sponsoredAdsBannerRendered`).
- Only when the old name says nothing (empty, "Trigger", "Custom Event", "Copy of …", "New trigger") is the action built from the configuration: the event name plus the first page/event condition (`ecom_event (add_to_cart)`).
- **No repeated words:** the vendor name (and its aliases: DY, FB, Facebook, AWin…), the trigger type, consent words and any segment already in the name are removed from the action. `CE - ecom_event (view_item) - MKT - ecom_event - view_item` → `CE - ecom_event (view_item) - MKT`; `WL - DY - All pages except PDP - Dynamic Yield` → `Dynamic Yield - WL - All pages except PDP`; `CE - sponsoredAdsBannerRendered - Criteo` → `Criteo - CE - sponsoredAdsBannerRendered`.
- **Consent** (`MKT`, `ANL`, `FUNC`) always last, only when a condition really tests consent. "OT", "OT Marketing", "OT Performance" and "OneTrust Marketing consent" are never kept. A trigger whose old name implied consent but has no consent condition gets the plain name (`OT - Awin Site Only` → `Awin - WL - Site only`) and is highlighted amber.
- **Exclude triggers** name what they exclude: `Exclude - <code> - <value of the condition>` (e.g. `Page Category contains blog` → `Exclude - PV - Blog`). When the value says nothing on its own (true, no, a regex), the variable name is added (`Exclude - CE - Listrak - Merchant ID no`).
- **Shared triggers:** a trigger used by tags of several vendors is `Trigger type - Action - Consent` – no vendor in front and no vendor name anywhere in the action (`PV - All Pages - for GA4` → `PV - All Pages`; `CE - ecom_event (add_to_cart) - Add To Cart for GA4` → `CE - ecom_event (add_to_cart)`). The consent ending stays when a condition tests consent (`CE - purchase - MKT`).
- `CE - OneTrustGroupsUpdated - DY - OneTrustConsent - MKT`, used only by Dynamic Yield → `Dynamic Yield - CE - OneTrustGroupsUpdated - OneTrustConsent - MKT`.

### Variables – `CODE - What it holds`

| Code | Variable type | Named from | Example |
| --- | --- | --- | --- |
| DLV | Data Layer Variable | the dataLayer key | `DLV - ecommerce.value` |
| CJS | Custom JavaScript | purpose (old name cleaned) | `Custom JS - Marketing Cookies Allowed` → `CJS - Marketing Cookies Allowed` |
| TPL | any custom-template variable | purpose | `Template - Marketing Cookies Allowed` → `TPL - Marketing Cookies Allowed` |
| CONST | Constant | purpose | `CONST - TikTok ID` |
| COOKIE | 1st-party cookie | the cookie name | `COOKIE - _dyid` |
| URL | URL | component / query key | `URL - Path`, `URL - Query - utm_source` |
| LT / RT | Lookup / RegEx table | purpose | `LT - Awin Account ID` |
| AEV | Auto-event | variable type | `AEV - Element` |
| JSV | JavaScript variable | the global name | `JSV - window.start.customer.email` |
| DOM | DOM element | purpose | `DOM - Marketing Consent Value` |
| ED | Event Data (sGTM) | key path | `ED - consent_given` |
| REF, CEV, UNDEF, UPD, GTES, GAS | referrer, custom event, undefined, user-provided data, event settings, GA settings | purpose | `GTES - GA4 Event Settings` |

Built-in variables are never renamed. Template and Custom JS consent variables are both kept and only renamed, never swapped.

## Same names in every brand – `--library`

Brands have the same kind of set-up, but not every brand has every tag, and new vendors, tags, triggers and variables keep being added. The library makes every brand use the same names:

1. **Reference brand first.** Rename the brand with the most complete set-up, fix its names (overrides), and keep its `<name>_library.json` as `brand_library.json`.
2. **Every next brand:** run with `--library brand_library.json`. An item **set up the same way** as one already in the library gets the library's name (Named from `library`, note "LIBRARY: same set-up as in <brand> – name reused"). Items the library does not know yet (a new vendor, a brand-only tag) are named by the rules as usual.
3. **Grow the library:** the run writes `<name>_library.json` = the library plus this brand's new set-ups. Replace `brand_library.json` with it, so a tag added in brand 5 gets the same name in brand 6. Repeat for every brand; re-running an already-renamed brand changes nothing.

"Set up the same way" is read from the configuration, never from names (names differ per brand):
- **Tag:** vendor (from the tag type or code), tag type or template name, its event (GA4 event name, the pixel's track call, the template's event field, the Floodlight group/activity, or a fingerprint of the Custom HTML code with numbers removed) and the set-ups of its firing triggers.
- **Trigger:** type, every condition (operator, value, and the set-up of the variable it tests), selector/interval settings; a trigger group by its members.
- **Variable:** type and key – the dataLayer key, cookie name, URL part, JS variable, Event Data key, DOM selector, the variable a lookup table reads, the code of a Custom JavaScript variable, or a template variable's settings.

Safe-guards: an item whose set-up appears twice in the same container is never renamed from the library; a brand's own entries never rename that brand; a consent variable only takes a consent name; names set by hand (`--overrides`) always win and also update the library. Priority: overrides → library → rules.

## Team rules – `--rules naming_rules.json` (optional)

`{"labels": {"html": "cHTML", "img": "Image Pixel", "template": "Template"}, "removeWords": ["iCrossing"], "folders": {"consent": "00 Consent & CMP", "shared": "01 Shared - Multiple Vendors", "novendor": "02 No Vendor - Helpers"}}` – any key left out keeps the standard. `removeWords` are removed from every tag and trigger action (whole words, with their separator). Consent endings (MKT, ANL, FUNC) and item codes (CE, PV, DLV…) are fixed.

## Folders – `--folders` (optional)

Every tag, trigger and variable is moved into one folder, decided by **which vendor's tags use it**:

| Folder | What goes in it |
| --- | --- |
| `<Vendor>` (e.g. `Meta`, `GA4`, `Hearst`) | tags of that vendor (also vendors not in the built-in list – from `--vendors`, or the first part of the tag name), and triggers / variables used only by that vendor's tags |
| `00 Consent & CMP` (or the team rule's name) | consent tags (OneTrust, Consent Mode), and consent variables (Marketing Cookies Allowed, OptanonConsent…) not owned by one vendor |
| `01 Shared - Multiple Vendors` | triggers and variables used by tags of two or more vendors (e.g. `CE - purchase - MKT`, `DLV - ecommerce.value`) |
| `02 No Vendor - Helpers` | tags with no vendor at all (e.g. `cHTML - SponsoredProductAddedToBasket`) and the triggers / variables only they use |

- A variable's users are found **directly and indirectly**: through the tags that use it, the triggers that use it (the vendors of those triggers' tags), and the variables that read it. `LT - DY - Section ID Table`, read only by Dynamic Yield variables, goes to `Dynamic Yield`.
- A folder `01 Utilities & Data Layer` left by an older run is removed once it is empty.
- The folders are the same on a first run and on a re-run of the renamed file.

## Clean-up – `--cleanup` (optional)

Deletes triggers and variables that nothing in use depends on. Tags are never deleted, and renamed items are never deleted – they keep their IDs (rename in place to see them as *Modified* in GTM).

- **A trigger is in use** if any tag fires or is blocked by it (**paused tags count as in use**), if a used trigger group contains it (followed through nested groups), or if a zone references it.
- **A variable is in use** if its `{{name}}` appears in a tag, a used trigger, a client, a transformation or a zone, or inside another variable that is in use (followed through every level: a lookup table that reads a variable that reads a cookie keeps all three).
- **Trigger groups are followed, not trusted:** a trigger that sits only inside trigger groups is kept only if at least one of those groups is itself in use. Checked cases:
  - trigger only inside a trigger group that no tag uses → the group **and** the trigger are deleted (e.g. `TG - Copy of Trigger test - No Consent - then consent` is deleted);
  - trigger inside an unused group **and** a used group → kept, because the used group needs it (e.g. `PV - All Pages - MKT - no consent` is in the deleted copy group and in `TG - No Consent - then consent`, which the Consent Mode Update tag uses – so it stays);
  - nested groups (unused group → group → trigger) → all three deleted;
  - a variable used only by a deleted trigger or group → deleted too.
  GTM's "References to this trigger" panel lists groups even when they are unused, so a trigger can show references there and still be deleted.
- Everything else is removed from the file and listed in the grey **Deleted – not used** sheet and in the rename map with Action "Deleted (not used)". Built-in variables are never touched.
- Run without `--cleanup` first if the user wants to review the list before anything is deleted; the review rows show which items would go.

## New vendors

A vendor that is not in the built-in list still follows every rule: its tags are `<Vendor> - <Tag type> - <Action>`, triggers used only by its tags start with `<Vendor> - `, and it gets its own folder.
- With `--vendors vendors.csv` the vendor is found by its words anywhere – tag name, template name or tag code (`ui.powerreviews.com` in the code → `Power Reviews - cHTML - …`, even when the old name was "Reviews widget - PDP"). Words are matched as whole words, case-insensitive; vendors in the file are checked before the built-in list.
- Without it, the first part of the old tag name is used as the vendor (`Hearst - Add To Cart` → `Hearst - cHTML - Add To Cart`).
- Keep one `vendors.csv` for all brands (it lists vendors, not names) and one overrides file per brand.

## What the script guarantees

- IDs, firing/blocking triggers, parameters and code are untouched; only `name` (and `parentFolderId` with `--folders`) change.
- Every `{{Old variable name}}` in tags, triggers, variables, clients and transformations is rewritten to the new name.
- Tag Sequencing references (`setupTag` / `teardownTag` tag names) are updated.
- Names are unique per item type; clashes are numbered and highlighted red as duplicates to delete.
- Nothing is replaced or merged. Duplicates and missing consent conditions are only reported. Without `--cleanup` nothing is deleted, so the import changes names alone; with `--cleanup` only the triggers and variables listed in *Deleted – not used* are removed.
- The file is import-safe: hidden template fields GTM rejects are removed (with the matching tag values, and the template's Gallery link, whose signature no longer matches), names never contain `{` `}` or line breaks, a variable never takes the name of a built-in variable, and anything else GTM may refuse is listed in the Import check.
- Running the script again on its own output changes nothing that is already standard.

## Testing the renamed file

GTM's **Import Container** matches items by **name**, not by ID. So when a renamed file is imported, every renamed item shows as **Deleted + Added**, even though its ID is unchanged. To see renamed items as **Modified**, rename them in place instead.

**Option A – rename in place (recommended, shows "Modified")**

1. Build the script: `python3 gen_apps_script.py <original_export.json> <name>_renamed.json <name>_rename_in_place.gs [--folders]` (in `scripts/` of the GitHub repo).
2. In GTM create a **new workspace** and note its number (the digits after `/workspaces/` in the address bar).
3. script.google.com → New project → paste the `.gs` file → set `WORKSPACE_ID` → Services → add **Tag Manager API**.
4. Run `run` with `DRY_RUN = true`, read the log, then set `DRY_RUN = false` and run again (re-run if it says "Time limit reached" until "ALL DONE").
5. Renamed items show as **Modified**, unused ones (with `--cleanup`) as **Deleted**. Only names, `{{variable}}` references, tag-sequencing names and (optionally) folders change; nothing is published. An item whose current name is not the expected old name is skipped and logged.

**Option B – import the renamed file**

1. GTM → Admin → **Import Container** → choose `<name>_renamed.json` (it carries the import fixes).
2. Workspace: **New**; option **Overwrite** – the new workspace becomes exactly this file; the live container is untouched. Do not use **Merge** for a full file: it adds the renamed items next to the old ones.
3. Renamed items appear as **Deleted + Added** (name-based matching) – expected; the result is the same container with new names.

**Then, for both options**

1. Preview the standard journey (home, PLP, PDP, add to cart, basket, checkout, purchase on staging): the same tags fire on the same events as in the live version.
2. Spot-check a few renamed variables inside Custom HTML tags – the new `{{names}}` resolve in Preview (no "undefined").
3. Publish only after sign-off; the previous version stays in Versions for rollback.

## Script – write to `gtm_rename.py`

```python

#!/usr/bin/env python3
"""GTM naming-convention renamer.

Reads a GTM container export (JSON), works out what every tag, trigger and
variable does from its configuration, renames it to the standard convention,
updates every reference ({{variable}} strings, Tag Sequencing tag names), and
writes: an import-ready container JSON, a rename map (CSV) and a summary (MD).

Usage:
  python3 gtm_rename.py <export.json> [--out DIR] [--folders] [--cleanup] [--library brand_library.json] [--overrides overrides.csv] [--vendors vendors.csv] [--rules naming_rules.json]
"""
import argparse, collections, copy, csv, json, os, re, sys

# ---------------------------------------------------------------- vendors
# (vendor, regex) – checked against: current name, then template name, then code/parameters
VENDORS = [
    ('Consent', r'consent mode|onetrust|optanon|didomi|\bcmp\b|cookie ?consent|cookiebot'),
    ('GA4', r'\bga4\b|google analytics 4|gtag\(.?config.?,\s*.?G-'),
    ('Google Ads', r'google ads|adwords|\baw-\d|conversion linker|remarketing|youtube micro'),
    ('Floodlight', r'floodlight|\bdc-\d|\bsa360\b|fls\.doubleclick|ad\.doubleclick'),
    ('CHEQ', r'\bcheq\b|clickcease'),
    ('Awin', r'\bawin\b|dwin1\.com|awin1\.com'),
    ('Meta', r'facebook|\bfbq\(|connect\.facebook|\bmeta\b|\bfb\b'),
    ('TikTok', r'tik ?tok|\bttq\.|analytics\.tiktok'),
    ('Pinterest', r'pinterest|pintrk'),
    ('Snapchat', r'snapchat|snaptr|sc-static\.net|\bsnap pixel'),
    ('Criteo', r'criteo|sponsoredads'),
    ('RTB House', r'rtb ?house|creativecdn'),
    ('Microsoft Ads', r'microsoft (ads|advertising)|\bbing\b|\buetq\b|bat\.bing|\buet\b'),
    ('X', r'twitter|\btwq\(|ads-twitter|static\.ads-twitter'),
    ('Reddit', r'reddit|\brdt\('),
    ('Listrak', r'listrak|_ltk\b'),
    ('Dynamic Yield', r'dynamic ?yield|\bDY\b|DY\.API|dy - '),
    ('Contentsquare', r'content ?square|_uxa'),
    ('Hotjar', r'hotjar'),
    ('Bazaarvoice', r'bazaar ?voice|\bbv[A-Z]\w+|\bBV\b'),
    ('RingCentral', r'ring ?central'),
    ('Partnerize', r'partnerize|prf\.hn'),
    ('Rakuten', r'rakuten|linksynergy'),
    ('CJ', r'commission junction|emjcd|\bcj\b'),
    ('TTD', r'trade ?desk|adsrvr|\bttd\b'),
    ('Xandr', r'xandr|appnexus|adnxs|\bmiq\b'),
    ('Line', r'\bline\b|line-scdn'),
    ('LinkedIn', r'linkedin|snap\.licdn'),
    ('Taboola', r'taboola'), ('Outbrain', r'outbrain'), ('Quantcast', r'quantcast'), ('Yahoo', r'yahoo'),
    ('AppsFlyer', r'appsflyer'), ('Kelkoo', r'kelkoo'), ('A8', r'\ba8\b'), ('Lunio', r'lunio'), ('UniDays', r'unidays'),
    ('Rokt', r'rokt'), ('Attentive', r'attentive'), ('Provenance', r'provenance'), ('Flixmedia', r'flixmedia|flix'),
    ('Qubit', r'qubit'), ('Yandex', r'yandex'), ('Baidu', r'baidu'), ('LiveRamp', r'liveramp'), ('AB Tasty', r'ab ?tasty'),
    ('intent.ly', r'intent\.?ly'), ('Kakao', r'kakao|arttrk'), ('Adobe', r'adobe'),
]
VENDOR_RX = [(v, re.compile(rx, re.I)) for v, rx in VENDORS]
BASE_VENDOR_RX = list(VENDOR_RX)
# words to strip from the start of an old name when re-using it (vendor aliases)
ALIASES = {
    'Meta': ['Facebook Pixel', 'Facebook', 'FB Pixel', 'FB', 'Meta Pixel', 'Meta'], 'TikTok': ['Tik Tok', 'TikTok', 'Tiktok'],
    'Contentsquare': ['Content Square', 'ContentSquare', 'Contentsquare', 'CS'], 'Dynamic Yield': ['Dynamic Yield', 'DY'],
    'Floodlight': ['Floodlight', 'FloodLight', 'SA360'], 'Awin': ['AWIN', 'AWin', 'Awin'], 'CHEQ': ['CHEQ', 'Cheq'],
    'GA4': ['GA4 Event', 'GA4', 'Google Analytics 4', 'GA'], 'Google Ads': ['Google Ads', 'AdWords', 'Adwords', 'GAds'],
    'Microsoft Ads': ['Microsoft Advertising', 'Microsoft Ads', 'Bing Ads', 'Bing', 'UET'], 'TTD': ['The Trade Desk', 'Trade Desk Pixel', 'Trade Desk', 'TTD'],
    'Xandr': ['MiQ/Xandr', 'Xandr', 'AppNexus', 'MiQ'], 'X': ['Twitter', 'X'], 'Bazaarvoice': ['Bazaar Voice', 'Bazaarvoice', 'BV'],
    'RTB House': ['RTB House', 'RTBHouse', 'RTB'], 'Line': ['LINE', 'Line'], 'RingCentral': ['Ring Central', 'RingCentral'],
    'Snapchat': ['Snapchat', 'Snap'], 'Consent': ['Consent', 'OneTrust', 'Onetrust', 'OT'], 'CJ': ['Commission Junction', 'CJ'],
}
BASE_ALIASES = copy.deepcopy(ALIASES)
NORM = [(r'\bTik ?Tok\b', 'TikTok'), (r'\bTiktok\b', 'TikTok'), (r'\bContent ?Square\b', 'Contentsquare'), (r'\bAW[Ii][Nn]\b', 'Awin'),
        (r'\bFloodLight\b', 'Floodlight'), (r'\bOnetrust\b', 'OneTrust'), (r'\bFacebook\b', 'Meta'), (r'\bBazaar Voice\b', 'Bazaarvoice'),
        (r'\bRing Central\b', 'RingCentral'), (r'\bCheq\b', 'CHEQ')]
GOOGLE = {'GA4', 'Google Ads', 'Floodlight'}

# ---------------------------------------------------------------- type codes
TAG_TYPES = {'html': 'Custom HTML', 'img': 'Custom Image', 'gaawe': 'GA4 Event', 'googtag': 'Google Tag', 'gaawc': 'GA4 Config',
             'awct': 'Google Ads Conversion', 'sp': 'Google Ads Remarketing', 'gclidw': 'Conversion Linker', 'awud': 'Google Ads User Data',
             'flc': 'Floodlight Counter', 'fls': 'Floodlight Sales', 'baut': 'Microsoft UET', 'crto': 'Criteo OneTag', 'pntr': 'Pinterest',
             'twitter_website_tag': 'X Base', 'hjtc': 'Hotjar', 'bzi': 'LinkedIn Insight'}
TRIG_CODE = {'PAGEVIEW': 'PV', 'DOM_READY': 'DOM', 'WINDOW_LOADED': 'WL', 'CUSTOM_EVENT': 'CE', 'CLICK': 'CLICK', 'LINK_CLICK': 'LINK',
             'ELEMENT_VISIBILITY': 'VIS', 'FORM_SUBMISSION': 'FORM', 'HISTORY_CHANGE': 'HIST', 'JS_ERROR': 'JSERR', 'TIMER': 'TIMER',
             'SCROLL_DEPTH': 'SCROLL', 'YOU_TUBE_VIDEO': 'YT', 'TRIGGER_GROUP': 'TG', 'INIT': 'INIT', 'CONSENT_INIT': 'CINIT',
             'SERVER_PAGEVIEW': 'SPV', 'ALWAYS': 'ALL'}
VAR_CODE = {'v': 'DLV', 'jsm': 'CJS', 'c': 'CONST', 'k': 'COOKIE', 'u': 'URL', 'smm': 'LT', 'remm': 'RT', 'd': 'DOM', 'j': 'JSV', 'aev': 'AEV',
            'f': 'REF', 'e': 'CEV', 'r': 'RAND', 'vis': 'VIS', 'gas': 'GAS', 'gtes': 'GTES', 'gtcs': 'GTCS', 'uv': 'UNDEF', 'awec': 'UPD',
            'ed': 'ED', 'ctv': 'CTV', 'dbg': 'DBG', 'cid': 'CID', 'rh': 'RH', 'gtm': 'GTM'}
TRIG_LABEL = {'PAGEVIEW': 'Page View', 'DOM_READY': 'DOM Ready', 'WINDOW_LOADED': 'Window Loaded', 'CUSTOM_EVENT': 'Custom Event', 'CLICK': 'Click',
              'LINK_CLICK': 'Link Click', 'ELEMENT_VISIBILITY': 'Element Visibility', 'FORM_SUBMISSION': 'Form Submit', 'HISTORY_CHANGE': 'History Change',
              'JS_ERROR': 'JS Error', 'TIMER': 'Timer', 'SCROLL_DEPTH': 'Scroll Depth', 'YOU_TUBE_VIDEO': 'YouTube Video', 'TRIGGER_GROUP': 'Trigger Group',
              'INIT': 'Initialization', 'CONSENT_INIT': 'Consent Initialization', 'SERVER_PAGEVIEW': 'Server Page View', 'ALWAYS': 'All Events'}
CONSENT_WORD = {'MKT': 'MKT', 'ANL': 'ANL', 'FUNC': 'FUNC'}
TAG_TYPE_SHORT = {'html': 'cHTML', 'img': 'Image Pixel', 'gaawe': 'Event', 'googtag': 'Google Tag', 'gaawc': 'Config', 'awct': 'Conversion', 'sp': 'Remarketing',
                  'gclidw': 'Conversion Linker', 'awud': 'User Data', 'flc': 'Counter', 'fls': 'Sales', 'baut': 'UET', 'crto': 'OneTag', 'pntr': 'Pixel',
                  'twitter_website_tag': 'Base Pixel', 'hjtc': 'Tracking Code', 'bzi': 'Insight Tag'}
VAR_LABEL = {'v': 'DLV', 'jsm': 'CJS', 'c': 'Constant', 'k': 'Cookie', 'u': 'URL', 'smm': 'Lookup', 'remm': 'RegEx Lookup', 'd': 'DOM Element', 'j': 'JS Variable',
             'aev': 'Auto Event', 'f': 'Referrer', 'e': 'Custom Event', 'r': 'Random', 'vis': 'Visibility', 'gas': 'GA Settings', 'gtes': 'Event Settings',
             'gtcs': 'Config Settings', 'uv': 'Undefined', 'awec': 'User Data', 'ed': 'Event Data', 'ctv': 'Container Version', 'dbg': 'Debug Mode',
             'cid': 'Container ID', 'rh': 'Request Header', 'gtm': 'GTM'}
OP_WORD = {'EQUALS': ('is', 'is not'), 'CONTAINS': ('contains', 'does not contain'), 'MATCH_REGEX': ('matches', 'does not match'),
           'STARTS_WITH': ('starts with', 'does not start with'), 'ENDS_WITH': ('ends with', 'does not end with'), 'CSS_SELECTOR': ('matches CSS', 'does not match CSS'),
           'GREATER': ('>', 'not >'), 'LESS': ('<', 'not <'), 'GREATER_OR_EQUALS': ('>=', 'not >='), 'LESS_OR_EQUALS': ('<=', 'not <=')}
VAR_PREFIX = ['DLV', 'DL', 'dataLayer', 'Data Layer', 'CJS', 'cjs', 'Custom JS', 'Custom JavaScript', 'JS', 'Cookie', '1st Party Cookie', 'COOKIE',
              'LT', 'Lookup', 'Lookup Table', 'GA4 LT', 'Regex', 'RegEx', 'RT', 'Template', 'TPL', 'const', 'Constant', 'CONST', 'AEV', 'URL',
              'DOM', 'JSV', 'ED', 'Event Data']
OLD_PREFIX = ['CE', 'OT Marketing Consent', 'OT Marketing', 'OT Performance consent', 'OT Performance',
              'OT CE', 'OT', 'Marketing OT', 'OneTrust Marketing Consent', 'Onetrust Marketing consent', 'OneTrust Performance Consent', 'Custom', 'custom', 'Pageview', 'Page View', 'PV', 'Trigger Group', 'TG',
              'Trigger', 'Event', 'Window Loaded', 'Window Load', 'windows load', 'Load', 'DOM Ready', 'Click', 'Initialization',
              'Consent Initialization', 'Timer', 'EXC', 'Exception', 'WL', 'Tag']
EVENT_LIKE = re.compile(r'event|name|action|page ?type|category|template', re.I)
JUNK = {'', 'undefined', 'true', 'false', 'null', '0', '1', '.*', 'none', 'no', 'yes'}
VAR_PREFIX += sorted(set(VAR_CODE.values()) - set(VAR_PREFIX))

# ---------------------------------------------------------------- re-runs: names already in the standard format
VENDOR_NAMES = sorted({v for v, _ in VENDORS} | {'Utility', 'Consent', 'Snapchat'}, key=len, reverse=True)
TYPE_WORDS = sorted(set(TAG_TYPE_SHORT.values()) | {'Template', 'Tag', 'HTML'}, key=len, reverse=True)
STD_TAG = re.compile(r'^(' + '|'.join(map(re.escape, VENDOR_NAMES)) + r') - (' + '|'.join(map(re.escape, TYPE_WORDS)) + r')(?: - |$)')
STD_TRIG = re.compile(r'^(?:Exclude - )?(?:[^-]{2,40}? - )?(?:Consent Initialization|Initialization|' + '|'.join(sorted(set(TRIG_CODE.values()), key=len, reverse=True)) + r') - ')  # [Vendor - ]Type - 
NUM_SUFFIX = re.compile(r'\s*\(\d+\)$')
STD_ANY = re.compile(r'^([^-]{2,40}?) - (cHTML|Image Pixel)(?: - |$)')   # '<any vendor> - cHTML - ...' (vendors not in the list)
STD_UTIL = re.compile(r'^(cHTML|Image Pixel) - ')                     # 'cHTML - <name>' (no vendor)
AGENCIES = ['iCrossing']                                              # agency names never kept in a tag name
SMALL_WORDS = {'a', 'an', 'and', 'or', 'of', 'to', 'in', 'on', 'for', 'the', 'by', 'with', 'from', 'at'}
EVENT_WRAPPERS = r'\b(?:ecom_event|elysiumEvent|custom_event|customEvent|PageLoad)\b'

def nice(s):
    """event-style text -> 'Add to Cart': no underscores, first letters capital, small words lower"""
    w = str(s).replace('_', ' ').split()
    return ' '.join(x if (len(x) > 1 and x.isupper()) else (x.lower() if i and x.lower() in SMALL_WORDS else x[:1].upper() + x[1:])
                    for i, x in enumerate(w))

def clean_event_text(s):
    """'errors - ecom_event (view_item) - ecom_event - view_item' -> 'View Item' (no wrappers, no brackets, no repeats)"""
    s = re.sub(EVENT_WRAPPERS, '', re.sub(r'^\s*(?:errors|Events)\s*(?:-\s*|$)', '', str(s)))
    segs = []
    for seg in re.split(r'\s+-\s+', s):
        seg = re.sub(r'[()]', ' ', seg).strip(' -')
        seg = nice(seg) if seg else ''
        if seg and seg.lower() not in [x.lower() for x in segs]: segs.append(seg)
    return ' - '.join(segs)
CONSENT_TAIL = re.compile(r'(?:(?:^|\s*-\s*)(?:MKT|ANL|FUNC))+$')

def std_core(old, kind):
    """strip the parts this script adds, so a renamed file renamed again gives the same names"""
    s = NUM_SUFFIX.sub('', str(old)).strip()
    if kind == 'tag':
        m = STD_TAG.match(s)
        if m: s = s[m.end():]
        else:
            m = STD_ANY.match(s) or STD_UTIL.match(s)
            if m: s = s[m.end():]
    elif kind == 'trigger':
        m = STD_TRIG.match(s)
        if m: s = s[m.end():]
    if kind == 'variable': return s
    return re.sub(r'\s*-\s*(?:MKT|ANL|FUNC)(?=\s*-)', '', CONSENT_TAIL.sub('', s)).strip()

def std_tag_name(name):
    """an older standard tag name brought up to date: HTML -> cHTML, no consent ending"""
    s = re.sub(r'^([^-]{2,40}?) - (?:HTML|cHTML)(?= - |$)', lambda m: m.group(1) + ' - ' + TAG_TYPE_SHORT['html'], str(name))
    return re.sub(r'\s*-\s*(?:MKT|ANL|FUNC)(?=\s*-|\s*\(\d+\)$|$)', '', s).strip()

def keep_existing(old, new):
    """old name already starts with the standard name (plus the user's own detail): keep it"""
    o = NUM_SUFFIX.sub('', str(old)).strip()
    if o.lower() == new.lower(): return new
    if sorted(o.lower().split(' - ')) == sorted(new.lower().split(' - ')): return o
    if not o.lower().startswith(new.lower() + ' - '): return new
    have = set(re.findall(r'\b(MKT|ANL|FUNC)\b', new))
    return new if set(re.findall(r'\b(MKT|ANL|FUNC)\b', o[len(new):])) - have else o

def tidy_action(core, vend, label, long_label, others=()):
    """trigger action: no consent words, no vendor words (the vendor goes first; a shared trigger names no vendor), no trigger-type words, nothing said twice"""
    aliases = sorted({a for v in ([vend] if vend else []) + list(others) for a in [v, *ALIASES.get(v, [])]} - {''}, key=len, reverse=True)
    skip = {re.sub(r'[\W_]+', '', label.lower()), re.sub(r'[\W_]+', '', long_label.lower())}
    segs, keys = [], []
    for seg in re.split(r'\s+-\s*|\s*-\s+', str(core)):
        x = seg.strip()
        if re.fullmatch(r'(?i)MKT|ANL|FUNC', x): continue
        for al in aliases: x = re.sub(r'(?i)(?:\b(?:for|by|via)\s+)?(?<![\w])' + re.escape(al) + r'(?![\w])', '', x)  # 'for GA4' goes with GA4
        x = re.sub(r'\(\s*\)', '', x); x = re.sub(r'\s{2,}', ' ', x).strip(' -')
        k = re.sub(r'[\W_]+', '', x.lower())
        if not k or k in skip or any(k in q for q in keys): continue
        for i, q in enumerate(keys):  # a later, more specific part replaces an earlier one it contains
            if q in k: segs[i] = None; keys[i] = ''
        segs.append(x); keys.append(k)
    out = ' - '.join(x for x in segs if x)
    return out or norm(core)

def find_unused(cv):
    """triggers and variables nothing in use depends on (all tags count as in use, paused ones too)"""
    tags, trigs, vars_ = cv.get('tag', []) or [], cv.get('trigger', []) or [], cv.get('variable', []) or []
    def trig_refs(o):
        out = []
        if isinstance(o, dict):
            for k, v in o.items():
                if k.endswith('TriggerId') or k == 'triggerIds': out += [str(x.get('value', x)) if isinstance(x, dict) else str(x) for x in (v if isinstance(v, list) else [v])]
                else: out += trig_refs(v)
        elif isinstance(o, list):
            for v in o: out += trig_refs(v)
        return out
    used_t = set(trig_refs(tags)) | set(trig_refs(cv.get('zone', []) or []))
    by_id = {str(t['triggerId']): t for t in trigs}
    todo = list(used_t)
    def members(t):
        return [str(x.get('value')) for p in t.get('parameter', []) or [] if p.get('key') == 'triggerIds' for x in p.get('list', []) or []]
    while todo:  # members of trigger groups that are in use
        t = by_id.get(todo.pop())
        if t and t.get('type') == 'TRIGGER_GROUP':
            for m in members(t):
                if m not in used_t: used_t.add(m); todo.append(m)
    refs = lambda o: set(re.findall(r'\{\{([^{}]+)\}\}', json.dumps(o, ensure_ascii=False)))
    used_v = refs(tags) | refs([t for t in trigs if str(t['triggerId']) in used_t])
    for k in ('client', 'transformation', 'zone'): used_v |= refs(cv.get(k, []) or [])
    by_name = {v['name']: v for v in vars_}
    todo = list(used_v)
    while todo:  # variables used by variables that are in use
        v = by_name.get(todo.pop())
        if v:
            for r in refs(v) - used_v: used_v.add(r); todo.append(r)
    return ([t for t in trigs if str(t['triggerId']) not in used_t], [v for v in vars_ if v['name'] not in used_v])

# ---------------------------------------------------------------- helpers
def norm(s):
    s = re.sub(r'\s*\|\s*(?![^()]*\))', ' - ', str(s)).replace(' > ', ' - ')  # '|' inside (...) is kept
    for a, b in NORM:
        s = re.sub(a, b, s)
    s = re.sub(r'\s*-\s*(-\s*)+', ' - ', s)
    s = re.sub(r'\s{2,}', ' ', s).strip(' -:_')
    return s

def strip_prefix(name, prefixes):
    s = str(name).strip(); changed = True
    while changed:
        changed = False
        for p in sorted(prefixes, key=len, reverse=True):
            m = re.match(r'^' + re.escape(p) + r'(\s*[-|:>_]\s*|\s+)', s, re.I)
            if m and len(s) > m.end():
                s = s[m.end():]; changed = True; break
    return s

def all_strings(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from all_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from all_strings(v)
    elif isinstance(obj, str):
        yield obj

def params(obj):
    """flatten GTM 'parameter' arrays to {key: value-or-structure}"""
    out = {}
    for p in obj.get('parameter', []) or []:
        k = p.get('key')
        if 'value' in p: out[k] = p['value']
        elif 'list' in p: out[k] = p['list']
        elif 'map' in p: out[k] = p['map']
    return out

def replace_refs(obj, mapping, counter):
    if not mapping: return obj
    if isinstance(obj, dict):
        return {k: replace_refs(v, mapping, counter) for k, v in obj.items()}
    if isinstance(obj, list):
        return [replace_refs(v, mapping, counter) for v in obj]
    if isinstance(obj, str) and '{{' in obj:
        def sub(m):
            old = m.group(1)
            if old in mapping:
                counter[0] += 1
                return '{{' + mapping[old] + '}}'
            return m.group(0)
        return re.sub(r'\{\{([^{}]+)\}\}', sub, obj)
    return obj

def detect_vendor(*texts):
    for t in texts:
        if not t: continue
        for v, rx in VENDOR_RX:
            if rx.search(t):
                return v
    return None

def short(s, n=40):
    s = re.sub(r'\s+', ' ', str(s)).strip()
    return s if len(s) <= n else s[:n - 1].rstrip() + '…'

def cond_parts(cond):
    """GTM condition → (op, left, right, negate)"""
    p = {x.get('key'): x.get('value') for x in cond.get('parameter', [])}
    neg = str(p.get('negate', 'false')).lower() == 'true'
    return cond.get('type', ''), p.get('arg0', ''), p.get('arg1', ''), neg

CONSENT_VAR = re.compile(r'marketing cookies allowed|marketing allowed|consent mode|consent_given|ad_storage|optanon|actual cookie consent|'
                         r'tracking allowed|functional cookies allowed|cookies allowed|didomi', re.I)

def consent_cat(left, right):
    l, r = left.lower(), str(right).lower()
    if not CONSENT_VAR.search(l): return None
    if 'marketing' in l or 'advertis' in l or 'ad_storage' in l or 'c0004' in r or 'consent_given' in l: return 'MKT'
    if 'analytic' in l or 'performance' in l or 'c0002' in r: return 'ANL'
    if 'functional' in l or 'c0003' in r: return 'FUNC'
    return 'MKT'

# ---------------------------------------------------------------- tag naming
TRACK_RX = [
    r"fbq\(\s*['\"](?:track|trackCustom)['\"]\s*,\s*['\"]([\w ]+)", r"ttq\.track\(\s*['\"](\w+)", r"snaptr\(\s*['\"]track['\"]\s*,\s*['\"](\w+)",
    r"pintrk\(\s*['\"]track['\"]\s*,\s*['\"](\w+)", r"rdt\(\s*['\"]track['\"]\s*,\s*['\"](\w+)", r"twq\(\s*['\"](?:event|track)['\"]\s*,\s*['\"]([\w-]+)",
    r"uetq\.push\(\s*['\"]event['\"]\s*,\s*['\"](\w+)", r"criteo_q\.push\([^)]*?event\s*:\s*['\"](\w+)", r"DY\.API\(\s*['\"]event['\"]\s*,\s*\{\s*name\s*:\s*['\"]([^'\"]+)",
    r"_uxa\.push\(\s*\[\s*['\"](\w+)", r"_ltk\.(\w+\.\w+)", r"window\._lt\(\s*['\"]send['\"]\s*,\s*['\"](\w+)",
]
TRACK_RX = [re.compile(x) for x in TRACK_RX]
LISTRAK_ACTION = {'Activity.AddProductBrowse': 'Product Browse', 'Alerts.AddAlertWithIdentifiers': 'Sign Up For Alert', 'SCA.Update': 'Email Capture'}
TEMPLATE_EVENT_KEYS = ['eventName', 'event_name', 'eventType', 'event', 'standardEventName', 'eventId', 'tagType', 'type']

def tag_action(tag, vendor, ttype, tname, old_rest):
    p = params(tag); t = tag.get('type', '')
    if t == 'gaawe':
        ev = str(p.get('eventName', ''))
        if ev and '{{' not in ev:
            if ev.lower() in ('errors', 'error', 'exception'):  # generic event: name it from its 'type' parameter
                rows = [{m.get('key'): m.get('value') for m in r.get('map', [])} for r in p.get('eventSettingsTable') or [] if isinstance(r, dict)]
                ty = next((r.get('parameterValue') for r in rows if r.get('parameter') == 'type' and '{{' not in str(r.get('parameterValue'))), '')
                return nice(ty) if ty else (clean_event_text(old_rest) or nice(ev)), 'config'
            return nice(ev), 'config'
        return (clean_event_text(old_rest) or 'Events'), 'name'
    if t in ('googtag', 'gaawc'):
        return 'Configuration', 'config'
    if t == 'gclidw': return '', 'config'
    if t == 'sp':
        a = old_rest if old_rest and not re.search('remarketing', old_rest, re.I) else ''
        return (clean_event_text(a) if re.search(r'_|' + EVENT_WRAPPERS, a) else a), 'config'
    if t == 'awct':
        cid = str(p.get('conversionId', '') or '')
        return 'Conversion' + (f' - {cid}' if cid.isdigit() else ''), 'config'
    if t in ('flc', 'fls'):
        a = strip_prefix(old_rest, ['Counter', 'Sales', 'Sales Tag'] + AGENCIES)
        for ag in AGENCIES: a = re.sub(r'\s*-?\s*\b' + re.escape(ag) + r'\b\s*-?\s*', ' - ', a).strip(' -')
        return (norm(a) or str(p.get('activityTag') or '')), 'config'
    code = ' '.join(all_strings(tag.get('parameter', [])))
    if vendor == 'Google Ads':  # Custom HTML Google Ads tags: conversion vs remarketing, from the code
        cid = re.search(r'google_conversion_id\s*=\s*[\'"]?(\d+)', code)
        if re.search(r'google_remarketing_only\s*=\s*true', code):
            rest = re.sub(r'^(Google\s+)?(Remarketing\s*-?\s*)?', '', old_rest, flags=re.I).strip(' -')
            return 'Remarketing' + (f' - {rest}' if rest else ''), 'code'
        if cid: return f'Conversion - {cid.group(1)}', 'code'
    if vendor == 'Criteo':  # the event after the set* calls says what the tag does
        cev = [e for e in re.findall(r"event\s*:\s*['\"](\w+)", code) if not e.startswith('set') and e != 'Product']
        if cev:
            e = cev[0]
            if old_rest.lower() == e.lower(): return old_rest, 'code'
            return {'viewPage': 'All pages', 'trackTransaction': 'trackTransaction (Conversion)'}.get(e, e), 'code'
    evs = []
    for rx in TRACK_RX:
        evs += rx.findall(code)
    evs = [e for e in dict.fromkeys(evs) if e]
    if vendor == 'Consent':
        return (old_rest or 'Consent'), 'name'
    if vendor == 'Awin':
        if t.startswith('cvt_') and re.search(r'consent', ttype, re.I) or re.search(r'consent', old_rest, re.I): return 'Consent Signals', 'config' if t.startswith('cvt_') else 'name'
        if t.startswith('cvt_') and re.search(r'master|journey', ttype, re.I) or re.search(r'js file|\bbase\b|master', old_rest, re.I): return 'MasterTag', 'config' if t.startswith('cvt_') else 'name'
        if re.search(r'sread|conversion|sale', code + old_rest, re.I): return 'Conversion', 'code'
    if t.startswith('cvt_'):
        for k in TEMPLATE_EVENT_KEYS:
            v = p.get(k)
            if isinstance(v, str) and v and '{{' not in v and len(v) < 40:
                return norm(v) + (' - ' + old_rest if old_rest and old_rest.lower() not in v.lower() else ''), 'config'
    if vendor == 'Contentsquare' and old_rest and evs:  # _uxa commands (trackPageview, setPIISelectors…) say how, the old name says what
        return old_rest, 'name'
    if vendor == 'Listrak' and evs:
        ev = LISTRAK_ACTION.get(evs[0])
        if ev: return ev, 'code'
        if old_rest: return old_rest, 'name'
    if evs:
        ev = evs[0] if len(evs) == 1 or evs[0].lower() != 'pageview' else evs[1] if len(evs) > 1 else evs[0]
        if re.search(r"fbq\(\s*['\"]init|ttq\.load|pintrk\(\s*['\"]load|snaptr\(\s*['\"]init|rdt\(\s*['\"]init", code) and ev.lower() in ('pageview', 'page'):
            ev = 'Base - PageView'
        return ev, 'code'
    if re.search(r"fbq\(\s*['\"]init|ttq\.load|pintrk\(\s*['\"]load|snaptr\(\s*['\"]init|rdt\(\s*['\"]init", code):
        return 'Base', 'code'
    rest = old_rest or ''
    if t == 'img':
        rest = norm(re.sub(r'\s*[-|]?\s*\b(image pixel|image|pixel)\b', '', rest, flags=re.I))
    return rest, 'name'


# ---------------------------------------------------------------- import safety
GTM_BUILTINS = {'Page URL', 'Page Hostname', 'Page Path', 'Referrer', 'Event', 'Click Element', 'Click Classes', 'Click ID', 'Click Target', 'Click URL',
                'Click Text', 'Form Element', 'Form Classes', 'Form ID', 'Form Target', 'Form URL', 'Form Text', 'Error Message', 'Error URL', 'Error Line',
                'Debug Mode', 'Random Number', 'Container ID', 'Container Version', 'Environment Name', 'HTML ID', 'New History Fragment', 'Old History Fragment',
                'New History State', 'Old History State', 'History Source', 'Video Provider', 'Video URL', 'Video Title', 'Video Duration', 'Video Percent',
                'Video Visible', 'Video Status', 'Video Current Time', 'Scroll Depth Threshold', 'Scroll Depth Units', 'Scroll Direction', 'Percent Visible',
                'On-Screen Duration', 'Client Name', 'Event Name', 'Query String', 'Request Method', 'Request Path', 'Server Container ID', 'Server Container URL'}
BUILTIN_TRIGGER_IDS = {'2147479553', '2147479572', '2147479573'}  # All Pages, Consent Initialization, Initialization
TD_SECTION = re.compile(r'(___TEMPLATE_PARAMETERS___\n\n)(.*?)(?=\n\n___\w+___|\Z)', re.S)

def safe_name(s):
    """GTM-safe name: no {{ }} (would read as a variable reference), no line breaks, single spaces"""
    s = re.sub(r'[{}]', '', str(s)).replace('\r', ' ').replace('\n', ' ')
    return re.sub(r'\s{2,}', ' ', s).strip() or 'Unnamed'

def import_check(cv):
    """Fix what GTM refuses on import and report what needs a look. Returns [(status, item, name, issue, action)]."""
    out = []
    used_by = collections.defaultdict(list)
    for x in (cv.get('tag', []) or []) + (cv.get('variable', []) or []):
        m = re.match(r'cvt_(?:\w+_)?(\d+)$', x.get('type', '') or '')
        if m: used_by[m.group(1)].append(x)
    for ct in cv.get('customTemplate', []) or []:
        td = ct.get('templateData', '') or ''
        if '___INFO___' not in td:
            out.append(('Check', 'Template', ct.get('name', ''), 'Template has no code (template_data missing ___INFO___) – GTM refuses the whole file: "Missing section ___INFO___"',
                        'Export the container again from GTM (Admin → Export Container) so the template code is included, then re-run')); continue
        m = TD_SECTION.search(td)
        if not m: continue
        try:
            plist = json.loads(m.group(2))
        except ValueError:
            out.append(('Check', 'Template', ct.get('name', ''), 'Template fields could not be read', 'Update the template from the Gallery, then export again')); continue
        removed = []
        def strip(ps):
            keep = []
            for q in ps:
                if q.get('type') == 'HIDDEN': removed.append(q.get('name', '')); continue
                if q.get('subParams'): q['subParams'] = strip(q['subParams'])
                keep.append(q)
            return keep
        plist = strip(plist)
        if not removed: continue
        ct['templateData'] = td[:m.start(2)] + json.dumps(plist, indent=2, ensure_ascii=False) + td[m.end(2):]
        had_gallery = ct.pop('galleryReference', None) is not None  # its signature no longer matches the edited template
        js = td.split('___SANDBOXED_JS_FOR_WEB_TEMPLATE___')[-1].split('\n\n___')[0] if '___SANDBOXED_JS_FOR_WEB_TEMPLATE___' in td else ''
        for x in used_by.get(str(ct.get('templateId')), []):
            x['parameter'] = [q for q in x.get('parameter', []) or [] if q.get('key') not in removed]
        for nm in removed:
            used = re.search(r'data\s*(\.\s*' + re.escape(nm) + r'\b|\[\s*[\'"]' + re.escape(nm) + r'[\'"]\s*\])', js)
            out.append(('Fixed', 'Template', ct.get('name', ''), f'Hidden field "{nm}" – GTM refuses hidden fields on import',
                        'Removed the field' + (' – the template code reads it: update the template from the Gallery before publishing' if used
                                               else ' (the template code never uses it, so nothing changes)')
                        + ('; the Gallery link was removed because GTM rejects a changed Gallery template – it imports as a custom template, re-link it later with "Update" from the Gallery if wanted' if had_gallery else '')))
    trig_ids = {str(t.get('triggerId')) for t in cv.get('trigger', []) or []}
    for tg in cv.get('tag', []) or []:
        for k in ('firingTriggerId', 'blockingTriggerId'):
            for i in tg.get(k, []) or []:
                if str(i) not in trig_ids and str(i) not in BUILTIN_TRIGGER_IDS:
                    out.append(('Check', 'Tag', tg['name'], f'Points to trigger ID {i}, which is not in the container', 'Re-select the trigger in GTM after import'))
    known = {v['name'] for v in cv.get('variable', []) or []} | {b.get('name', '') for b in cv.get('builtInVariable', []) or []} | GTM_BUILTINS
    seen = set()
    for key, item in (('tag', 'Tag'), ('trigger', 'Trigger'), ('variable', 'Variable')):
        for x in cv.get(key, []) or []:
            for ref in re.findall(r'\{\{([^{}]+)\}\}', json.dumps(x, ensure_ascii=False)):
                if ref not in known and not ref.startswith('_') and (item, x['name'], ref) not in seen:
                    seen.add((item, x['name'], ref))
                    out.append(('Check', item, x['name'], f'Uses {{{{{ref}}}}}, which is not a variable in the container (already missing before the rename)', 'Create or enable the variable, or fix the reference'))
    for key, item in (('tag', 'Tag'), ('trigger', 'Trigger'), ('variable', 'Variable')):
        names = collections.Counter(x['name'].lower() for x in cv.get(key, []) or [])
        for n, c in names.items():
            if c > 1: out.append(('Check', item, n, f'{c} items share this name', 'Rename one of them before import'))
    return out

def set_vendors(custom):
    """the user's own vendors [(name, 'word, word')] - checked before the built-in list"""
    global VENDOR_NAMES, STD_TAG
    word_rx = lambda w: r'(?<![A-Za-z0-9])' + re.escape(w.strip()) + r'(?![A-Za-z0-9])'
    VENDOR_RX[:] = []
    ALIASES.clear(); ALIASES.update(copy.deepcopy(BASE_ALIASES))
    for name, match in custom:
        name = str(name).strip()
        if not name: continue
        words = [w.strip() for w in [name] + str(match or '').split(',') if w.strip()]
        VENDOR_RX.append((name, re.compile('|'.join(map(word_rx, words)), re.I)))
        ALIASES[name] = list(dict.fromkeys(ALIASES.get(name, []) + words))
    VENDOR_RX.extend(BASE_VENDOR_RX)
    VENDOR_NAMES = sorted({v for v, _ in VENDOR_RX} | {'Utility', 'Consent', 'Snapchat'}, key=len, reverse=True)
    STD_TAG = re.compile(r'^(' + '|'.join(map(re.escape, VENDOR_NAMES)) + r') - (' + '|'.join(map(re.escape, TYPE_WORDS)) + r')(?: - |$)')

RULES = {}
DEFAULT_RULES = {'labels': {'html': 'cHTML', 'img': 'Image Pixel', 'template': 'Template'}, 'removeWords': ['iCrossing'],
                 'folders': {'consent': '00 Consent & CMP', 'shared': '01 Shared - Multiple Vendors', 'novendor': '02 No Vendor - Helpers'}}
def set_rules(r):
    """the team's own naming rules: tag type labels, words never kept in a name, folder names"""
    global TYPE_WORDS, STD_ANY, STD_UTIL, AGENCIES
    r = r or {}
    lab = {k: (str((r.get('labels') or {}).get(k) or '').strip() or v) for k, v in DEFAULT_RULES['labels'].items()}
    fol = {k: (str((r.get('folders') or {}).get(k) or '').strip() or v) for k, v in DEFAULT_RULES['folders'].items()}
    words = list(dict.fromkeys([w.strip() for w in DEFAULT_RULES['removeWords'] + list(r.get('removeWords') or []) if str(w).strip()]))
    RULES.clear(); RULES.update({'labels': lab, 'folders': fol, 'removeWords': words})
    TAG_TYPE_SHORT['html'] = lab['html']; TAG_TYPE_SHORT['img'] = lab['img']
    TYPE_WORDS = sorted(set(TAG_TYPE_SHORT.values()) | {lab['template'], 'Template', 'Tag', 'HTML', 'cHTML', 'Image Pixel'}, key=len, reverse=True)
    pix = '|'.join(map(re.escape, sorted(set(TYPE_WORDS) - {'Tag'}, key=len, reverse=True)))
    STD_ANY = re.compile(r'^([^-]{2,40}?) - (' + pix + r')(?: - |$)')
    STD_UTIL = re.compile(r'^(' + pix + r') - ')
    AGENCIES = words

def strip_words(text):
    """words the team never keeps in a name (agency names, old labels) are removed with their separator"""
    for w in RULES.get('removeWords', []):
        text = re.sub(r'(?i)\s*-?\s*(?<![A-Za-z0-9])' + re.escape(w) + r'(?![A-Za-z0-9])\s*-?\s*', ' - ', text)
    return norm(text).strip(' -') if RULES.get('removeWords') else text

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('export'); ap.add_argument('--out', default='.'); ap.add_argument('--folders', action='store_true'); ap.add_argument('--overrides', help='CSV with columns Item,Old name,New name to force specific names')
    ap.add_argument('--cleanup', action='store_true', help='delete triggers and variables that nothing in use depends on')
    ap.add_argument('--rules', help='JSON with the team rules: {"labels": {"html": "cHTML", "img": "Image Pixel", "template": "Template"}, "removeWords": ["iCrossing"], "folders": {"consent": "...", "shared": "...", "novendor": "..."}}')
    ap.add_argument('--library', help='brand library JSON from an earlier run (<name>_library.json): the same set-up gets the same name as in the other brands')
    ap.add_argument('--vendors', help='CSV with columns Vendor,Match (comma-separated words that identify the vendor in names, template names or code)')
    a = ap.parse_args()
    set_rules(json.load(open(a.rules, encoding='utf-8')) if a.rules else {})
    set_vendors([(r.get('Vendor', ''), r.get('Match', '')) for r in csv.DictReader(open(a.vendors, encoding='utf-8'))] if a.vendors else [])
    OV = {(r['Item'].strip().lower(), r['Old name'].strip()): r['New name'].strip() for r in csv.DictReader(open(a.overrides, encoding='utf-8')) if r.get('New name')} if a.overrides else {}
    raw = json.load(open(a.export, encoding='utf-8'))
    data = copy.deepcopy(raw)
    cv = data.get('containerVersion', data)
    removed = []  # (kind, id, name, type) deleted by --cleanup
    if a.cleanup:
        un_t, un_v = find_unused(cv)
        drop_t = {id(x) for x in un_t}; drop_v = {id(x) for x in un_v}
        removed = [('Trigger', x['triggerId'], x['name'], x.get('type', '')) for x in un_t] + [('Variable', x['variableId'], x['name'], x.get('type', '')) for x in un_v]
        cv['trigger'] = [x for x in cv.get('trigger', []) or [] if id(x) not in drop_t]
        cv['variable'] = [x for x in cv.get('variable', []) or [] if id(x) not in drop_v]
    tags, trigs, vars_ = cv.get('tag', []) or [], cv.get('trigger', []) or [], cv.get('variable', []) or []
    tmpl = {}
    for ct in cv.get('customTemplate', []) or []:
        tmpl[str(ct.get('templateId'))] = ct.get('name', '')
    def tmpl_name(t):
        m = re.match(r'cvt_(?:\w+_)?(\d+)$', t or '')
        return tmpl.get(m.group(1), '') if m else ''

    # ---- vendor per tag
    tag_vendor, tag_type_name = {}, {}
    for tg in tags:
        t = tg.get('type', ''); tn = tmpl_name(t)
        tag_type_name[tg['tagId']] = TAG_TYPES.get(t) or (f'Template: {tn}' if tn else t)
        fixed = {'gaawe': 'GA4', 'googtag': 'GA4', 'gaawc': 'GA4', 'awct': 'Google Ads', 'sp': 'Google Ads', 'gclidw': 'Google Ads', 'awud': 'Google Ads',
                 'flc': 'Floodlight', 'fls': 'Floodlight', 'baut': 'Microsoft Ads', 'crto': 'Criteo', 'twitter_website_tag': 'X', 'hjtc': 'Hotjar', 'bzi': 'LinkedIn'}.get(t)
        code = ' '.join(all_strings(tg.get('parameter', [])))[:20000]
        mstd = STD_TAG.match(tg['name'])
        many = STD_ANY.match(tg['name']) if not mstd else None
        tag_vendor[tg['tagId']] = fixed or (mstd.group(1) if mstd else None) or detect_vendor(tg['name'], tn, code) or \
            (many.group(1) if many and not STD_UTIL.match(tg['name']) else None) or 'Utility'

    # ---- trigger usage
    fire_by = collections.defaultdict(list); block_by = collections.defaultdict(list)
    for tg in tags:
        for i in tg.get('firingTriggerId', []) or []: fire_by[str(i)].append(tg['tagId'])
        for i in tg.get('blockingTriggerId', []) or []: block_by[str(i)].append(tg['tagId'])
    in_group = set()
    for tr in trigs:
        if tr.get('type') == 'TRIGGER_GROUP':
            for p in tr.get('parameter', []):
                if p.get('key') == 'triggerIds':
                    for x in p.get('list', []): in_group.add(str(x.get('value')))
                    for tid in [str(x.get('value')) for x in p.get('list', [])]:
                        fire_by[tid] += fire_by.get(str(tr['triggerId']), [])

    rows = []  # (kind, id, old, new, basis, note)

    # ---- variables (needed for trigger consent detection on new names, but conditions use old names)
    new_var = {}
    for vr in vars_:
        t = vr.get('type', ''); p = params(vr); old = std_core(vr['name'], 'variable')
        code = 'TPL' if t.startswith('cvt_') else VAR_CODE.get(t, 'VAR')
        rest = norm(strip_prefix(re.sub(r'^Lookup\s*\(([^)]*)\)\s*-\s*', r'\1 - ', old), VAR_PREFIX))
        basis = 'name'
        if t == 'v' and p.get('name'): rest, basis = str(p['name']), 'config'
        elif t == 'k' and p.get('name'): rest, basis = str(p['name']), 'config'
        elif t == 'u':
            comp = str(p.get('component', 'URL')).title().replace('_', ' ')
            q = p.get('queryKey'); rest, basis = (f'Query - {q}' if q else comp), 'config'
        elif t == 'aev' and p.get('varType'): rest, basis = str(p['varType']).title().replace('_', ' '), 'config'
        elif t == 'j' and p.get('name'): rest, basis = str(p['name']), 'config'
        elif t == 'ed' and p.get('keyPath'): rest, basis = str(p['keyPath']), 'config'
        if t == 'jsm' and re.search(r'marketing cookies allowed', old, re.I): rest = 'Marketing Cookies Allowed'
        new_var[vr['variableId']] = [f'{code} - {rest}', basis, norm(strip_prefix(old, VAR_PREFIX))]

    # ---- tags (before triggers: a trigger's vendor is the vendor of the tags that use it)
    new_tag = {}
    for tg in tags:
        v = tag_vendor[tg['tagId']]; old = std_core(tg['name'], 'tag'); t = tg.get('type', '')
        old_rest = norm(strip_prefix(old, ALIASES.get(v, [v]) + ['Tag'])) if v != 'Consent' else norm(old)
        if old_rest.lower() == v.lower(): old_rest = ''
        act, basis = tag_action(tg, v, tag_type_name[tg['tagId']], tmpl_name(t), old_rest)
        act = norm(act)
        if t in ('flc', 'fls') and not old and STD_TAG.match(tg['name']): act = ''
        act = strip_words(re.sub(r'\s*-\s*(?:MKT|ANL|FUNC)(?=\s*-|$)', '', act).strip(' -'))   # consent endings live on triggers only
        typ = RULES['labels']['template'] if t.startswith('cvt_') or t == 'awct' else TAG_TYPE_SHORT.get(t, 'Tag')
        if v == 'Utility':  # no vendor found: the old name's first part is the vendor ('Hearst - cHTML - Add To Cart')
            first, _, more = act.partition(' - ')
            name = (f'{first} - {typ} - {more}' if more else f'{act} - {typ}') if act else typ
        else:
            parts = []
            for x in (v, typ, act):
                if x and not any(p_.lower() == x.lower() for p_ in parts): parts.append(x)
            name = ' - '.join(parts)
        new_tag[tg['tagId']] = [name, basis, old_rest]

    owner = {}  # the vendor a tag belongs to: a vendor not in the list is the first part of its new name ('Hearst - cHTML - ...')
    for tg in tags:
        v = tag_vendor[tg['tagId']]; n = new_tag[tg['tagId']][0]
        n = OV.get(('tag', tg['name'])) or OV.get(('tag', n)) or n  # a brand override decides the final name, so also the vendor
        m = STD_ANY.match(n) if v == 'Utility' and not STD_UTIL.match(n) and not STD_UTIL.match(tg['name']) else None  # 'cHTML - X' stays vendor-less
        owner[tg['tagId']] = m.group(1) if m else v

    owner_label = lambda k: 'No vendor' if owner[k] == 'Utility' else owner[k]

    # ---- triggers
    def var_label(l): return norm(strip_prefix(str(l).replace('{', '').replace('}', ''), VAR_PREFIX))
    def cond_words(op, l, r, neg):
        w = OP_WORD.get(op, (op.lower(), 'not ' + op.lower()))
        return f'{var_label(l)} {w[1] if neg else w[0]} {short(r, 30)}'
    def clean_old(old):
        c = norm(strip_prefix(old, OLD_PREFIX))
        c = re.sub(r'\s*[-|]?\s*\b(OT |OneTrust )?(Marketing|Performance)( consent)?\b', '', c, flags=re.I).strip(' -') or c
        c = re.sub(r'\s*[-|]?\s*\bOT\b\s*[-|]?\s*', ' ', c).strip(' -') or c
        c = re.sub(r'\s*[-|]?\s*\btrigger\b', '', c, flags=re.I).strip(' -') or c
        return norm(c)
    is_any_event = lambda cp: '_event' in cp[1] and cp[2] in ('.*', '.+')
    GENERIC_OLD = {'', 'trigger', 'event', 'events', 'customevent', 'allevents', 'pageview', 'pv', 'ce', 'wl', 'dom', 'click', 'new', 'test', 'initialisation', 'consentinitialisation'}
    def good_old(oc, label, t):
        k = re.sub(r'[\W_]+', '', str(oc).lower())
        if str(oc).startswith('(') or k in GENERIC_OLD or k in (re.sub(r'[\W_]+', '', label.lower()), re.sub(r'[\W_]+', '', TRIG_LABEL.get(t, '').lower())): return False
        return not re.fullmatch(r'(?i)(?:copy of\s+)?(?:untitled|new)\s*trigger.*', str(oc))
    new_trig, trig_cats, trig_parts = {}, {}, {}
    for tr in trigs:
        tid = str(tr['triggerId']); t = tr.get('type', ''); old = std_core(tr['name'], 'trigger')
        exc = bool((not fire_by.get(tid)) and block_by.get(tid) and tid not in in_group)
        label = TRIG_LABEL[t] if t in ('INIT', 'CONSENT_INIT') else TRIG_CODE.get(t, t[:5] or 'TRG')
        conds = (tr.get('customEventFilter', []) or []) + (tr.get('filter', []) or []) + (tr.get('autoEventFilter', []) or [])
        cats, ev, detail, basis = set(), '', '', 'name'
        for c in tr.get('customEventFilter', []) or []:
            op, l, r, neg = cond_parts(c)
            if '_event' in l and r: ev = 'All Events' if r in ('.*', '.+') else short(r, 32); basis = 'config'
        for c in conds:
            op, l, r, neg = cond_parts(c)
            cc = consent_cat(l, r)
            if cc and not neg: cats.add(cc)
            elif cc and neg and op in ('EQUALS', 'CONTAINS') and str(r).lower() == 'true': pass
            elif not detail and not neg and op in ('EQUALS', 'CONTAINS', 'MATCH_REGEX', 'STARTS_WITH', 'ENDS_WITH') and '_event' not in l \
                    and str(r).strip().lower() not in JUNK and len(str(r)) <= 32 and (EVENT_LIKE.search(l) or re.search(r'page|path|url', l, re.I)):
                detail = str(r).strip('/').replace('|', '/'); basis = 'config'
        oc = clean_old(old)
        has_plain = any(not consent_cat(cond_parts(c)[1], cond_parts(c)[2]) and not is_any_event(cond_parts(c)) for c in conds)
        if exc:
            what = []
            for c in [c for c in conds if not is_any_event(cond_parts(c))][:2]:
                op, l, r, neg = cond_parts(c)
                v = str(r).strip().strip('/^$').replace('|', ' / ')
                good = v and v.lower() not in JUNK and len(v) <= 30 and not re.search(r'[\\\[\]()*+?]', v)
                what.append(v[0].upper() + v[1:] if good else var_label(l) + (' ' + v if v and len(v) <= 30 else ''))
            core = ' - '.join(what) if what else oc
            if what: basis = 'config'
        elif t == 'TRIGGER_GROUP':
            core = norm(strip_prefix(old, OLD_PREFIX))
        elif good_old(oc, label, t):  # the old name says what the trigger is for: keep its words, only fit them into the format
            core = oc
        elif t == 'CUSTOM_EVENT':
            core = (ev or oc) + (f' ({detail})' if detail else '')
            if detail and not ev and detail.lower() in oc.lower(): core = oc
        elif t in ('PAGEVIEW', 'DOM_READY', 'WINDOW_LOADED', 'INIT', 'CONSENT_INIT'):
            if not has_plain: core = 'All Pages'
            elif detail and detail.lower() in oc.lower(): core = oc
            else: core = detail or oc
        else:
            core = detail if detail and detail.lower() not in oc.lower() else oc
        users = {owner[x] for x in fire_by.get(tid, []) + block_by.get(tid, [])}
        vend = next(iter(users)) if len(users) == 1 else ''
        cond_text = ' '.join(all_strings(conds))
        # a trigger used only by one vendor's tags belongs to that vendor (Vendor - Type - Action)
        vpart = vend if not exc and vend and vend not in GOOGLE | {'Utility', 'Consent'} else ''
        others = tuple(sorted(users - {'Utility', 'Consent'})) if len(users) > 1 and not exc else ()  # shared by several vendors: Type - Action, no vendor words
        core = strip_words(core) or core
        if t != 'TRIGGER_GROUP':
            act = tidy_action(core, vpart, label, TRIG_LABEL.get(t, ''), others)
            if vpart and act == norm(core) and not tidy_action(core, '', label, TRIG_LABEL.get(t, '')).replace(vpart, '').strip(' -'):
                vpart = ''  # the action is only the vendor's name: keep it as the action, no vendor in front
            core = act if act != norm(core) or not vpart else core
            core = tidy_action(core, vpart, label, TRIG_LABEL.get(t, ''), others)
        suf = '' if exc else ''.join(f' - {CONSENT_WORD[c]}' for c in sorted(cats))
        trig_cats[tid] = cats
        note = ''
        if re.search(r'marketing|performance|\bOT\b', old, re.I) and not cats and t != 'TRIGGER_GROUP' and not exc:
            note = 'NO CONSENT: old name implied a consent gate but no consent condition was found – renamed without a consent ending'
        if tid in in_group and not fire_by.get(tid): note = (note + '; ' if note else '') + 'Member of a trigger group'
        nm = f'Exclude - {label} - {norm(core)}' if exc else (f'{vpart} - ' if vpart else '') + f'{label} - {norm(core)}{suf}'  # Vendor - Type - Action - Consent
        new_trig[tid] = [nm, basis, oc, note]
        trig_parts[tid] = (vpart, label, core, suf, exc, TRIG_LABEL.get(t, ''), others)

    # ---- uniqueness per entity type
    rerun = bool(tags) and sum(1 for x in tags if STD_TAG.match(x['name'])) >= 0.6 * len(tags)  # file was already renamed once
    def dedupe(items, extra_fn, orig=None, combine=None, same=None, rank=None, detail=None):
        """same: set-up key (true duplicates are only numbered); rank: 0 active, 1 paused (active keeps the clean name)"""
        rk = rank or (lambda k: 0)
        groups = collections.defaultdict(list)
        for k, v in items.items(): groups[v[0].lower()].append(k)
        for key, ks in groups.items():
            if len(ks) == 1: continue
            sk = collections.Counter(same(k) for k in ks) if same else None
            cand = [k for k in ks if not sk or sk[same(k)] == 1]  # identical set-ups are duplicates, not different items
            if rank:
                act = [k for k in ks if rk(k) == 0]
                cand = [k for k in cand if rk(k) == 0] if len(act) > 1 else []  # paused leftovers never get extra words
            if orig and rerun:  # re-run: names that were already made unique by an earlier run are kept
                o = {k: NUM_SUFFIX.sub('', orig[k]).strip() for k in ks}
                ol = [x.lower() for x in o.values()]
                for k in list(cand):
                    if o[k].lower().split(' - ')[0] == key.split(' - ')[0] and o[k].lower() != key and ol.count(o[k].lower()) == 1 \
                            and o[k].lower() not in {items[j][0].lower() for j in items if j not in ks} and items[k][1] != 'override':
                        items[k][0] = o[k]; cand.remove(k)
                if len(cand) < 2: cand = []
            extras = {k: (extra_fn(k) or '') for k in cand}
            vals = [e.lower() for e in extras.values()]
            for k in cand:
                e = extras[k]
                if e and vals.count(e.lower()) == 1 and e.lower() not in items[k][0].lower():
                    items[k][0] = combine(k, e) if combine else f'{items[k][0]} - {e}'
            if detail and same:  # still the same name but set up differently: a word from the set-up tells them apart
                sub = collections.defaultdict(list)
                for k in ks: sub[items[k][0].lower()].append(k)
                for kk in sub.values():
                    if len(kk) < 2 or len({same(k) for k in kk}) < 2: continue
                    det = {k: detail(k, kk) for k in kk}
                    dl = [x.lower() for x in det.values()]
                    for k in kk:
                        e = det[k]
                        if e and dl.count(e.lower()) == 1 and e.lower() not in items[k][0].lower():
                            items[k][0] = combine(k, e) if combine else f'{items[k][0]} - {e}'
        final = collections.Counter(); first = {}; first_k = {}
        used = {v[0].lower() for v in items.values()}
        order = sorted(items, key=lambda k: rk(k))  # stable: active items first, then paused copies
        for k in order:
            v = items[k]
            base = v[0]; final[base.lower()] += 1
            if final[base.lower()] == 1: first[base.lower()] = base; first_k[base.lower()] = k
            elif rk(k):  # paused copy of a live item: kept, renamed to the format with ' - Paused'
                pn = combine(k, 'Paused') if combine else f'{base} - Paused'
                n2, i = pn, 1
                while n2.lower() in used: i += 1; n2 = f'{pn} ({i})'
                v[0] = n2; used.add(n2.lower())
                v.append(f'PAUSED copy of live "{first[base.lower()]}" – renamed to the format and kept')
            else:
                v[0] = f'{base} ({final[base.lower()]})'
                if same and same(k) != same(first_k[base.lower()]):  # different set-up: not a duplicate
                    v.append(f'NAME CLASH with "{first[base.lower()]}" – different set-up, keep both and check the name')
                else: v.append(f'DUPLICATE of "{first[base.lower()]}" – re-point anything using it, then delete')
        return items
    if a.overrides:
        ov = {(r['Item'].strip().lower(), r['Old name'].strip()): r['New name'].strip() for r in csv.DictReader(open(a.overrides, encoding='utf-8')) if r.get('New name')}
        for kind, items, src, idk in (('tag', new_tag, tags, 'tagId'), ('trigger', new_trig, trigs, 'triggerId'), ('variable', new_var, vars_, 'variableId')):
            for x in src:
                it = items[str(x[idk]) if kind == 'trigger' else x[idk]]
                o = ov.get((kind, x['name'])) or ov.get((kind, it[0]))  # matches the current name or the standard name
                if o: it[0] = o; it[1] = 'override'
    def trig_combine(k, e):  # extra words go inside the action, the consent stays last
        vp, lab, core, suf, exc, long, oth = trig_parts[k]
        if exc or lab == 'TG': return f'{new_trig[k][0]} - {e}'
        return (f'{vp} - ' if vp else '') + f'{lab} - ' + norm(tidy_action(f'{core} - {e}', vp, lab, long, oth)) + suf
    def keep_trigger(k, old, new):
        """an earlier run's extra detail is kept, but put back in the right place (consent last, no repeats)"""
        o = NUM_SUFFIX.sub('', str(old)).strip()
        if o.lower() == new.lower() or not o.lower().startswith(new.lower() + ' - '): return new
        extra = o[len(new) + 3:]
        if set(re.findall(r'\b(MKT|ANL|FUNC)\b', extra)) - set(re.findall(r'\b(MKT|ANL|FUNC)\b', new)): return new
        return trig_combine(k, extra)
    trig_by_id = {str(t['triggerId']): t for t in trigs}
    def trig_key(name):  # 'Criteo - CE - Add To Cart - MKT (2)' -> 'ce - add to cart'
        t = NUM_SUFFIX.sub('', re.sub(r'^[^-]+ - ', '', str(name))).strip()
        return re.sub(r'\s+', ' ', re.sub(r'\s*-\s*(?:MKT|ANL|FUNC)(?=\s*-|$)', '', t)).strip().lower()
    def trig_text_added(tg, new):
        o = NUM_SUFFIX.sub('', std_tag_name(tg['name'])).strip()
        if not o.lower().startswith(new.lower() + ' - '): return False
        extra = re.sub(r'\s+', ' ', o[len(new) + 3:]).strip().lower()
        keys = set()
        for f in tg.get('firingTriggerId') or []:
            f = str(f)
            if f in new_trig: keys.add(trig_key(new_trig[f][0]))
            if f in trig_by_id: keys.add(trig_key(trig_by_id[f]['name']))
        return extra in keys
    for items, src, idk in ((new_tag, tags, 'tagId'), (new_trig, trigs, 'triggerId'), (new_var, vars_, 'variableId')):
        for x in src:
            v = items[str(x[idk]) if idk == 'triggerId' else x[idk]]
            if v[1] == 'override': continue
            if idk == 'triggerId' and not trig_parts[str(x[idk])][4] and trig_parts[str(x[idk])][1] != 'TG':
                v[0] = keep_trigger(str(x[idk]), x['name'], v[0])  # Vendor - Type - Action - Consent, nothing repeated
            elif idk == 'tagId' and trig_text_added(x, v[0]):
                pass  # an earlier run added the trigger's name to tell copies apart: dropped, duplicates are numbered instead
            else:
                v[0] = keep_existing(std_tag_name(x['name']) if idk == 'tagId' else x['name'], v[0])
    # ---- brand library: the same set-up gets the same name in every brand
    FP_PARAMS = {'elementSelector', 'elementId', 'selectorType', 'eventName', 'interval', 'limit', 'verticalThresholdsPercent', 'horizontalThresholdsPercent', 'triggerStartOption'}
    def fnv(text):  # short stable hash (same in the page)
        h = 0x811c9dc5
        for ch in str(text): h = ((h ^ ord(ch)) * 0x01000193) & 0xffffffff
        return format(h, '08x')
    code_key = lambda c: fnv(re.sub(r'\d+', '', re.sub(r'\s+', '', re.sub(r'\{\{[^{}]+\}\}', '{{}}', re.sub(r'/\*.*?\*/|//[^\n]*', '', str(c), flags=re.S)))).lower())  # variable names inside differ per brand
    def var_key(vr):
        t = vr.get('type', ''); p = params(vr)
        if t in ('v', 'k', 'j'): return str(p.get('name', ''))
        if t == 'jsm':
            js = re.sub(r'\{\{[^{}]+\}\}', '{{}}', re.sub(r'\s+', '', re.sub(r'/\*.*?\*/|//[^\n]*', '', str(p.get('javascript', '')), flags=re.S)))
            return 'js:' + code_key(js) + ('' if len(js) >= 60 else '|n:' + new_var[vr['variableId']][0].lower())  # short code alone says too little
        if t == 'd': return f"{p.get('selectorType', '')}|{p.get('elementId', '')}{p.get('elementSelector', '')}|{p.get('attributeName', '')}"
        if t in ('smm', 'remm'): return 'in:' + str(p.get('input', ''))
        if t == 'u': return f"{p.get('component', 'URL')}|{p.get('queryKey', '')}"
        if t == 'aev': return str(p.get('varType', ''))
        if t == 'ed': return str(p.get('keyPath', ''))
        return 'p:' + code_key(';'.join(f'{k}={v}' for k, v in sorted(p.items()) if isinstance(v, str)))  # templates, constants, other types: their settings
    var_fp = {vr['name']: f"V|{tmpl_name(vr.get('type', '')) or vr.get('type', '')}|{var_key(vr)}" for vr in vars_}
    raw_in = {vr['name']: str(params(vr).get('input', '')) for vr in vars_ if vr.get('type') in ('smm', 'remm')}
    for n, i in raw_in.items():  # a lookup table is known by the variable it reads
        var_fp[n] = var_fp[n].split('|in:')[0] + '|in:' + re.sub(r'\{\{([^{}]+)\}\}', lambda m: '{{' + var_fp.get(m.group(1), 'B:' + m.group(1)) + '}}', i)
    ref_fp = lambda v: re.sub(r'\{\{([^{}]+)\}\}', lambda m: '{{' + var_fp.get(m.group(1), 'B:' + m.group(1)) + '}}', str(v))
    trig_by = {str(t['triggerId']): t for t in trigs}; tfp_memo = {}
    def trig_fp(tid, depth=0):
        tid = str(tid)
        if tid in tfp_memo: return tfp_memo[tid]
        t = trig_by.get(tid)
        if not t or depth > 8: return 'B|' + tid
        if t.get('type') == 'TRIGGER_GROUP':
            ms = [str(x.get('value')) for p in t.get('parameter', []) or [] if p.get('key') == 'triggerIds' for x in p.get('list', []) or []]
            f = 'T|TRIGGER_GROUP|' + ','.join(sorted(trig_fp(m, depth + 1) for m in ms))
        else:
            conds = []
            for lst in ('customEventFilter', 'filter', 'autoEventFilter'):
                for c in t.get(lst, []) or []:
                    op, l, r, neg = cond_parts(c)
                    conds.append(f'{lst}:{op}|{ref_fp(l)}|{ref_fp(r)}|{int(neg)}')
            ps = [f"{p.get('key')}={ref_fp(p.get('value', ''))}" for p in t.get('parameter', []) or [] if p.get('key') in FP_PARAMS and 'value' in p]
            f = f"T|{t.get('type', '')}|" + ';'.join(sorted(conds)) + '|' + ';'.join(sorted(ps))
        tfp_memo[tid] = f
        return f
    def tag_fp(tg):
        t = tg.get('type', ''); p = params(tg)
        if t == 'gaawe': sig = str(p.get('eventName', ''))
        elif t in ('flc', 'fls'): sig = f"{p.get('groupTag', '')}|{p.get('activityTag', '')}"
        elif t.startswith('cvt_'): sig = '|'.join(str(p.get(k)) for k in TEMPLATE_EVENT_KEYS if isinstance(p.get(k), str) and '{{' not in p.get(k))
        else:
            code = ' '.join(all_strings(tg.get('parameter', [])))
            sig = ','.join(dict.fromkeys(e for rx in TRACK_RX for e in rx.findall(code) if e)) or ('code:' + code_key(code) if t in ('html', 'img', 'pntr') else '')
        return f"G|{tag_vendor[tg['tagId']] if tag_vendor[tg['tagId']] in VENDOR_NAMES else 'Utility'}|{tmpl_name(t) or t}|{sig}|" + ','.join(sorted(trig_fp(i) for i in tg.get('firingTriggerId', []) or []))
    fps = {'tag': {tg['tagId']: tag_fp(tg) for tg in tags}, 'trigger': {str(t['triggerId']): trig_fp(t['triggerId']) for t in trigs},
           'variable': {vr['variableId']: var_fp[vr['name']] for vr in vars_}}
    LIB = json.load(open(a.library, encoding='utf-8')) if a.library else {}
    brand_id = cv.get('container', {}).get('publicId', '') or os.path.splitext(os.path.basename(a.export))[0]
    for kind, items in (('tag', new_tag), ('trigger', new_trig), ('variable', new_var)):
        n_fp = collections.Counter(fps[kind].values())
        for k, it in items.items():
            f = fps[kind][k]; e = (LIB.get(kind) or {}).get(f)
            if it[1] == 'override' or not e or n_fp[f] > 1 or not e.get('name') or e['name'] == it[0] or e.get('id') == brand_id: continue  # a brand's own names come from its own run
            if kind == 'variable' and bool(CONSENT_VAR.search(it[0])) != bool(CONSENT_VAR.search(e['name'])): continue  # a consent variable keeps a consent name
            it[0] = e['name']; it[1] = 'library'
            msg = f"LIBRARY: same set-up as in {e.get('brand') or 'another brand'} – name reused"
            if kind == 'trigger': it[3] = (it[3] + '; ' if it[3] else '') + msg
            else: it.append(msg)
    paused_tag = {x['tagId']: bool(x.get('paused')) for x in tags}
    def trig_rank(k):  # 1 = used only by paused tags (a leftover copy); unused or used by an active tag = 0
        us = fire_by.get(k, []) + block_by.get(k, [])
        return 1 if us and all(paused_tag.get(t) for t in us) else 0
    dedupe(new_trig, lambda k: new_trig[k][2], {str(x['triggerId']): x['name'] for x in trigs}, trig_combine, lambda k: fps['trigger'][k], trig_rank)
    def tag_extra(k):
        tg = next(x for x in tags if x['tagId'] == k)
        f = (tg.get('firingTriggerId') or [None])[0]
        if f and str(f) in new_trig:
            return re.sub(r'\s*-\s*(?:MKT|ANL|FUNC)(?=\s*-|$)', '', NUM_SUFFIX.sub('', re.sub(r'^[^-]+ - ', '', new_trig[str(f)][0])).strip())
        return new_tag[k][2]
    dedupe(new_tag, tag_extra, {x['tagId']: std_tag_name(x['name']) for x in tags}, None, lambda k: fps['tag'][k], lambda k: 1 if paused_tag.get(k) else 0)
    ref_names = lambda o: {m for s_ in all_strings(o) for m in re.findall(r'\{\{([^{}]+)\}\}', s_)}
    vref = {vr['name']: ref_names(vr) for vr in vars_}
    def reach(seed):  # variables reached from these items, also through other variables
        got = set(seed); todo = list(got)
        while todo:
            for m in vref.get(todo.pop(), ()):
                if m not in got: got.add(m); todo.append(m)
        return got
    live_v = reach(set().union(*[ref_names(x) for x in tags if not paused_tag.get(x['tagId'])],
                               *[ref_names(x) for x in trigs if not trig_rank(str(x['triggerId']))],
                               *[ref_names(cv.get(k_, []) or []) for k_ in ('client', 'transformation', 'zone')]))
    paused_v = reach(set().union(*[ref_names(x) for x in tags if paused_tag.get(x['tagId'])],
                                 *[ref_names(x) for x in trigs if trig_rank(str(x['triggerId']))]))
    old_var = {x['variableId']: x['name'] for x in vars_}
    var_rank = lambda k: 1 if old_var[k] in paused_v and old_var[k] not in live_v else 0  # used only by paused tags
    var_by_id = {x['variableId']: x for x in vars_}
    JS_WORDS = {'function', 'return', 'var', 'let', 'const', 'true', 'false', 'null', 'undefined', 'typeof', 'catch', 'try', 'else', 'window',
                'document', 'this', 'new', 'length', 'indexOf', 'split', 'join', 'push', 'toString', 'toLowerCase', 'toUpperCase', 'replace', 'match'}
    STR_RX = re.compile(r"'(?:\\.|[^'\\])*'" + '|' + r'"(?:\\.|[^"\\])*"')
    def js_code(k):  # Custom JavaScript without comments, string contents and {{variable}} references
        c = re.sub(r'/\*.*?\*/|//[^\n]*', '', str(params(var_by_id[k]).get('javascript', '')), flags=re.S)
        return re.sub(r'\{\{[^{}]+\}\}', ' ', STR_RX.sub("''", c))
    def js_refs(k):  # variables the code reads, without their type prefix ('RT - ProdId from URL' -> 'ProdId from URL')
        return [norm(strip_prefix(r, VAR_PREFIX)) for r in dict.fromkeys(re.findall(r'\{\{([^{}]+)\}\}', str(params(var_by_id[k]).get('javascript', ''))))]
    def js_tokens(k):
        c = js_code(k)
        local = set(re.findall(r'\b(?:var|let|const|function)\s+([A-Za-z_$][\w$]*)', c)) | set(re.findall(r'\bcatch\s*\(\s*([A-Za-z_$][\w$]*)', c))
        return [t for t in dict.fromkeys(re.findall(r'[A-Za-z_$][\w$]{3,}', c)) if t not in JS_WORDS and t not in local]
    def var_detail(k, group):  # what only this variable's code uses: a variable it reads, else a property it reads, else a name in its code
        if var_by_id[k].get('type') != 'jsm': return ''
        oth = [j for j in group if j != k and var_by_id[j].get('type') == 'jsm']
        o_refs = {r.lower() for j in oth for r in js_refs(j)}
        refs = [r for r in js_refs(k) if r.lower() not in o_refs]
        if refs: return refs[0]
        o_tok = {t for j in oth for t in js_tokens(j)}
        uniq = [t for t in js_tokens(k) if t not in o_tok]
        c = js_code(k)
        props = [t for t in uniq if re.search(r'(?<!window)\.' + re.escape(t) + r'\b', c)]
        return (props or uniq or [''])[0]
    dedupe(new_var, lambda k: new_var[k][2], {x['variableId']: x['name'] for x in vars_}, None, lambda k: fps['variable'][k], var_rank, var_detail)
    builtin = {b.get('name', '').lower() for b in cv.get('builtInVariable', []) or []}
    for items in (new_tag, new_trig, new_var):
        for v in items.values(): v[0] = safe_name(v[0])
    for v in new_var.values():
        if v[0].lower() in builtin: v[0] += ' - Custom'
    brand = cv.get('container', {}).get('name', '') or os.path.splitext(os.path.basename(a.export))[0]
    library = copy.deepcopy(LIB)
    for kind, items in (('tag', new_tag), ('trigger', new_trig), ('variable', new_var)):
        n_fp = collections.Counter(fps[kind].values()); lk = library.setdefault(kind, {})
        for k, it in items.items():
            f = fps[kind][k]
            if n_fp[f] > 1 or any('DUPLICATE' in str(x) for x in it[2:]): continue
            if f not in lk or it[1] == 'override' or lk[f].get('id') == brand_id: lk[f] = {'name': it[0], 'brand': brand, 'id': brand_id}

    # ---- apply
    var_map = {}
    for vr in vars_:
        nn = new_var[vr['variableId']][0]
        if nn != vr['name']: var_map[vr['name']] = nn
    tag_map = {}
    for tg in tags:
        nn = new_tag[tg['tagId']][0]
        if nn != tg['name']: tag_map[tg['name']] = nn
    counter = [0]
    for key in ('tag', 'trigger', 'variable', 'client', 'transformation', 'zone'):
        if key in cv:
            cv[key] = replace_refs(cv[key], var_map, counter)
    tags, trigs, vars_ = cv.get('tag', []) or [], cv.get('trigger', []) or [], cv.get('variable', []) or []
    seq = 0
    for tg in tags:
        for k in ('setupTag', 'teardownTag'):
            for s in tg.get(k, []) or []:
                if s.get('tagName') in tag_map: s['tagName'] = tag_map[s['tagName']]; seq += 1

    for tg in tags:
        n, basis, *rest = new_tag[tg['tagId']]
        rows.append(('Tag', tg['tagId'], tg['name'], n, owner_label(tg['tagId']), tag_type_name[tg['tagId']], basis, '; '.join(x for x in rest[1:] if x)))
        tg['name'] = n
    for tr in trigs:
        n, basis, _, note, *more = new_trig[str(tr['triggerId'])]
        rows.append(('Trigger', tr['triggerId'], tr['name'], n, '', tr.get('type', ''), basis, '; '.join(x for x in [note] + more if x)))
        tr['name'] = n
    for vr in vars_:
        n, basis, *rest = new_var[vr['variableId']]
        rows.append(('Variable', vr['variableId'], vr['name'], n, '', vr.get('type', ''), basis, '; '.join(x for x in rest[1:] if x)))
        vr['name'] = n

    for kind, rid, nm, typ in removed:
        rows.append((kind, rid, nm, '(deleted)', '', typ, 'cleanup', 'UNUSED: no tag, trigger group or used variable depends on it – deleted'))

    # ---- optional vendor folders
    made_folders = []
    # folder per item: always worked out (Folder column); only applied to the file with --folders
    SHARED, NOVENDOR, CONSENTF = RULES['folders']['shared'], RULES['folders']['novendor'], RULES['folders']['consent']
    def fname(v): return CONSENTF if v == 'Consent' else (NOVENDOR if v == 'Utility' else v)
    def pick(us, consent=False):  # one vendor -> its folder; several -> Shared; none -> No Vendor
        if len(us) == 1: return fname(next(iter(us)))
        if consent: return fname('Consent')
        return SHARED if len(us) > 1 else NOVENDOR
    fvend = owner; want = {}
    for tg in tags: want[('Tag', str(tg['tagId']))] = fname(fvend[tg['tagId']])
    var_users = collections.defaultdict(set)  # vendors whose tags use the variable - directly, through a trigger, or through another variable
    refs_in = lambda o: set(re.findall(r'\{\{([^{}]+)\}\}', json.dumps(o, ensure_ascii=False)))
    for tr in trigs:
        us = {fvend[x] for x in fire_by.get(str(tr['triggerId']), []) + block_by.get(str(tr['triggerId']), [])}
        want[('Trigger', str(tr['triggerId']))] = pick(us)
        for m in refs_in(tr): var_users[m] |= us
    for tg in tags:
        for m in refs_in(tg): var_users[m].add(fvend[tg['tagId']])
    var_refs = {vr['name']: refs_in(vr) for vr in vars_}
    changed = True
    while changed:
        changed = False
        for n, rs in var_refs.items():
            for m in rs:
                if not var_users[n] <= var_users[m]: var_users[m] |= var_users[n]; changed = True
    for vr in vars_: want[('Variable', str(vr['variableId']))] = pick(var_users.get(vr['name'], set()), bool(CONSENT_VAR.search(vr['name'])))
    items = (('Tag', tags, 'tagId'), ('Trigger', trigs, 'triggerId'), ('Variable', vars_, 'variableId'))
    if a.folders:
        folders = cv.setdefault('folder', [])
        by_name = {f['name']: f['folderId'] for f in folders}
        nxt = max([int(f['folderId']) for f in folders] + [int(x.get('tagId', 0)) for x in tags] + [int(x.get('triggerId', 0)) for x in trigs] +
                  [int(x.get('variableId', 0)) for x in vars_] + [0]) + 1
        acc, con = cv.get('accountId', ''), cv.get('containerId', '')
        def ensure(n):
            nonlocal nxt
            if n not in by_name:
                folders.append({'accountId': acc, 'containerId': con, 'folderId': str(nxt), 'name': n}); by_name[n] = str(nxt); made_folders.append(n); nxt += 1
            return by_name[n]
        for k, src, idk in items:
            for x in src: x['parentFolderId'] = ensure(want[(k, str(x[idk]))])
        used_f = {x.get('parentFolderId') for x in tags + trigs + vars_}  # the old catch-all folder from an earlier run goes once it is empty
        cv['folder'] = [f for f in folders if not (f['name'] == '01 Utilities & Data Layer' and f['folderId'] not in used_f)]
    fname_by_id = {str(f['folderId']): f['name'] for f in cv.get('folder', []) or []}
    folder_of = {}
    for k, src, idk in items:
        for x in src: folder_of[(k, str(x[idk]))] = (fname_by_id.get(str(x['parentFolderId']), '') if x.get('parentFolderId') else 'Unfiled')
    rows = [r + (('' if r[6] == 'cleanup' else folder_of.get((r[0], str(r[1])), '')),) for r in rows]

    fixes = import_check(cv)

    # ---- write
    os.makedirs(a.out, exist_ok=True)
    base = os.path.splitext(os.path.basename(a.export))[0]
    jout = os.path.join(a.out, f'{base}_renamed.json'); cout = os.path.join(a.out, f'{base}_rename_map.csv'); mout = os.path.join(a.out, f'{base}_summary.md')
    json.dump(data, open(jout, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    lout = os.path.join(a.out, f'{base}_library.json')
    json.dump(library, open(lout, 'w', encoding='utf-8'), indent=1, ensure_ascii=False, sort_keys=True)
    with open(cout, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['Item', 'ID', 'Old name', 'New name', 'Vendor', 'Type', 'Changed', 'Named from', 'Note', 'Folder'])
        for r in rows: w.writerow([r[0], r[1], r[2], r[3], r[4], r[5], 'Yes' if r[2] != r[3] else 'No', r[6], r[7], r[8]])

    esc = lambda x: str(x).replace('|', '\\|')
    def cnt(kind, cond=lambda r: True): return sum(1 for r in rows if r[0] == kind and cond(r))
    ch = lambda r: r[2] != r[3] and 'UNUSED' not in r[7]
    lines = [f'# GTM naming review – {cv.get("container", {}).get("name", base)}', '',
             f'Container {cv.get("container", {}).get("publicId", "")} · export {os.path.basename(a.export)}', '',
             '## What was done', '',
             '| Item | Total | Renamed | Already standard | Named from config/code | Named from old name (review) |', '| --- | --- | --- | --- | --- | --- |']
    for k in ('Tag', 'Trigger', 'Variable'):
        lines.append(f'| {k}s | {cnt(k)} | {cnt(k, ch)} | {cnt(k, lambda r: not ch(r))} | {cnt(k, lambda r: r[6] in ("config", "code"))} | {cnt(k, lambda r: r[6] == "name")} |')
    lines += ['', f'- {counter[0]} variable references ({{{{…}}}}) updated inside tags, triggers and variables.',
              f'- {seq} Tag Sequencing references (set-up / clean-up tag names) updated.',
              f'- {sum(1 for r in rows if "DUPLICATE" in r[7])} duplicates numbered (2), (3)… – delete after re-pointing (red in the Excel summary).',
              f'- {sum(1 for r in rows if "NO CONSENT" in r[7])} triggers were named as consent-gated but have no consent condition (amber in the Excel summary).']
    if removed: lines.append(f'- {sum(1 for r in removed if r[0] == "Trigger")} triggers and {sum(1 for r in removed if r[0] == "Variable")} variables deleted because nothing in use depends on them (grey in the Excel summary).')
    if made_folders: lines.append(f'- {len(made_folders)} vendor folders created: ' + ', '.join(made_folders) + '.')
    lines.append(f'- Import check: {sum(1 for f in fixes if f[0] == "Fixed")} problem(s) GTM would refuse were fixed, {sum(1 for f in fixes if f[0] == "Check")} item(s) to check.')
    if fixes:
        lines += ['', '## Import check', '', '| Status | Item | Name | Issue | What was done |', '| --- | --- | --- | --- | --- |'] + \
                 [f'| {f[0]} | {f[1]} | {esc(f[2])} | {esc(f[3])} | {esc(f[4])} |' for f in fixes[:200]]
    vc = collections.Counter(owner_label(x['tagId']) for x in tags)
    lines += ['', '## Tags by vendor', '', '| Vendor | Tags |', '| --- | --- |'] + [f'| {v} | {n} |' for v, n in vc.most_common()]
    flagged = [r for r in rows if r[7]]
    if flagged:
        lines += ['', '## Check these', '', '| Item | Old name | New name | Why |', '| --- | --- | --- | --- |'] + \
                 [f'| {r[0]} | {esc(r[2])} | {esc(r[3])} | {esc(r[7])} |' for r in flagged[:200]]
    review = [r for r in rows if r[6] == 'name' and ch(r)]
    if review:
        lines += ['', '## Named from the old name (no config signal) – quick review', '', '| Item | Old name | New name |', '| --- | --- | --- |'] + \
                 [f'| {r[0]} | {esc(r[2])} | {esc(r[3])} |' for r in review[:200]]
    lines += ['', '## Sample of changes', '', '| Item | Old name | New name |', '| --- | --- | --- |'] + \
             [f'| {r[0]} | {esc(r[2])} | {esc(r[3])} |' for r in [r for r in rows if ch(r)][:40]]
    lines += ['', '## Import to test', '', '1. GTM → Admin → Import Container → choose the _renamed.json file.',
              '2. Workspace: **New** (e.g. "Naming review – test"). Option: **Overwrite** (the new workspace becomes exactly this file).',
              '3. Preview the standard journey; the same tags must fire as before – only names change.',
              '4. Publish only after review; the old version stays in Versions for rollback.']
    open(mout, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    xout = os.path.join(a.out, f'{base}_summary.xlsx')
    try:
        write_xlsx(xout, cv, base, rows, counter[0], seq, made_folders, collections.Counter(owner_label(x['tagId']) for x in tags), fixes)
    except ImportError:
        xout = None
    print(json.dumps({'xlsx': xout, 'json': jout, 'library': lout, 'from_library': sum(1 for r in rows if r[6] == 'library'), 'map': cout, 'summary': mout, 'renamed': sum(1 for r in rows if ch(r)), 'total': len(rows), 'refs': counter[0], 'seq': seq, 'fixed': sum(1 for f in fixes if f[0] == 'Fixed'), 'check': sum(1 for f in fixes if f[0] == 'Check')}))

def write_xlsx(path, cv, base, rows, refs, seq, made_folders, vendors, fixes=()):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    GREY = PatternFill('solid', fgColor='D9D9D9'); RED = PatternFill('solid', fgColor='F8CBAD'); AMBER = PatternFill('solid', fgColor='FFE699'); BLUE = PatternFill('solid', fgColor='DDEBF7')
    HEAD = PatternFill('solid', fgColor='1F3A5F'); HF = Font(bold=True, color='FFFFFF'); B = Font(bold=True)
    def action(r):
        if 'DUPLICATE' in r[7]: return 'Delete (duplicate) – re-point first'
        if 'NAME CLASH' in r[7]: return 'Check name – different set-up, keep both'
        if 'NO CONSENT' in r[7]: return 'Rename + add consent condition (Phase 4)'
        if 'UNUSED' in r[7]: return 'Deleted (not used)'
        return 'Rename' if r[2] != r[3] else 'No change'
    def fill_for(r):
        return RED if 'DUPLICATE' in r[7] else AMBER if 'NO CONSENT' in r[7] else GREY if 'UNUSED' in r[7] else None
    def table(ws, r0, header, data, fills=None, widths=None):
        for j, h in enumerate(header, 1):
            c = ws.cell(r0, j, h); c.fill = HEAD; c.font = HF; c.alignment = Alignment(wrap_text=True, vertical='top')
        for i, row in enumerate(data, r0 + 1):
            for j, v in enumerate(row, 1):
                c = ws.cell(i, j, v); c.alignment = Alignment(wrap_text=True, vertical='top')
                if fills and fills[i - r0 - 1]: c.fill = fills[i - r0 - 1]
        return r0 + len(data)
    wb = Workbook(); ws = wb.active; ws.title = 'Summary'
    ws['A1'] = f'GTM naming review – {cv.get("container", {}).get("name", base)}'; ws['A1'].font = Font(bold=True, size=14)
    ws['A2'] = f'Container {cv.get("container", {}).get("publicId", "")}'
    ch = lambda r: r[2] != r[3] and 'UNUSED' not in r[7]
    data = []
    for k in ('Tag', 'Trigger', 'Variable'):
        rr = [r for r in rows if r[0] == k]
        data.append([k + 's', len(rr), sum(map(ch, rr)), sum(1 for r in rr if not ch(r)), sum(1 for r in rr if 'DUPLICATE' in r[7]),
                     sum(1 for r in rr if 'NO CONSENT' in r[7]), sum(1 for r in rr if r[6] == 'name' and ch(r))])
    end = table(ws, 4, ['Item', 'Total', 'Renamed', 'Already standard', 'Duplicates (delete)', 'No consent condition', 'Named from old name (review)'], data)
    notes = [f'{refs} variable references ({{{{…}}}}) updated inside tags, triggers and variables.', f'{seq} Tag Sequencing references updated.']
    if made_folders: notes.append(f'{len(made_folders)} vendor folders created: ' + ', '.join(made_folders))
    un = [r for r in rows if 'UNUSED' in r[7]]
    if un: notes.append(f'{sum(1 for r in un if r[0] == "Trigger")} triggers and {sum(1 for r in un if r[0] == "Variable")} variables deleted – nothing in use depends on them (sheet "Deleted – not used").')
    notes.append(f'Import check: {sum(1 for f in fixes if f[0] == "Fixed")} problem(s) GTM would refuse were fixed, {sum(1 for f in fixes if f[0] == "Check")} item(s) to check (sheet "Import check").')
    r = end + 2
    for n in notes: ws.cell(r, 1, '• ' + n); r += 1
    r += 1; ws.cell(r, 1, 'Colour key').font = B; r += 1
    for f, t in ((RED, 'Red – duplicate of another item: re-point anything that uses it to the original, then delete'),
                 (AMBER, 'Amber – trigger was named as consent-gated (Marketing / Performance) but has no consent condition: renamed to the format, add the consent condition'),
                 (BLUE, 'Blue – named from the old name only (no config signal): quick review'),
                 (GREY, 'Grey – deleted: no tag, trigger group or used variable depends on it')):
        ws.cell(r, 1).fill = f; ws.cell(r, 2, t); r += 1
    r += 1; ws.cell(r, 1, 'Tags by vendor').font = B
    table(ws, r + 1, ['Vendor', 'Tags'], [[v, n] for v, n in vendors.most_common()])
    for col, w in zip('ABCDEFG', (16, 10, 10, 16, 18, 20, 26)): ws.column_dimensions[col].width = w
    ws.column_dimensions['B'].width = 12
    hdr = ['Item', 'ID', 'Old name', 'New name', 'Folder', 'Vendor', 'Type', 'Changed', 'Named from', 'Action', 'Note']
    def sheet(title, sel):
        w = wb.create_sheet(title)
        data = [[r[0], r[1], r[2], r[3], r[8], r[4], r[5], 'Yes' if ch(r) else 'No', r[6], action(r), r[7]] for r in sel]
        fills = [fill_for(r) or (BLUE if r[6] == 'name' and ch(r) else None) for r in sel]
        last = table(w, 1, hdr, data, fills)
        w.freeze_panes = 'A2'; w.auto_filter.ref = f'A1:K{max(last, 1)}'
        for j, wd in enumerate((10, 8, 45, 45, 26, 16, 22, 9, 11, 32, 60), 1): w.column_dimensions[get_column_letter(j)].width = wd
    order = lambda r: (0 if 'DUPLICATE' in r[7] else 1 if 'NO CONSENT' in r[7] else 2 if 'UNUSED' in r[7] else 3, r[0], r[3].lower())
    sheet('Rename Map', sorted(rows, key=order))
    sheet('Duplicates – delete', [r for r in rows if 'DUPLICATE' in r[7]])
    sheet('No consent condition', [r for r in rows if 'NO CONSENT' in r[7]])
    sheet('Deleted – not used', [r for r in rows if 'UNUSED' in r[7]])
    GREEN = PatternFill('solid', fgColor='E2EFDA')
    w = wb.create_sheet('Import check')
    last = table(w, 1, ['Status', 'Item', 'Name', 'Issue', 'What was done'], [list(f) for f in fixes] or [['OK', '', '', 'Nothing GTM would refuse', '']],
                 [GREEN if f[0] == 'Fixed' else AMBER for f in fixes] or [GREEN])
    w.freeze_panes = 'A2'
    for j, wd in enumerate((9, 10, 45, 60, 60), 1): w.column_dimensions[get_column_letter(j)].width = wd
    wb.save(path)

if __name__ == '__main__':
    main()

```
