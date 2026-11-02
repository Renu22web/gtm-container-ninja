#!/usr/bin/env python3
"""Build a Google Apps Script that applies a GTM rename IN PLACE through the Tag Manager API,
so GTM shows renamed items as Modified (an import matches by name, so renames show as Deleted + Added).

Usage: python3 gen_apps_script.py <original_export.json> <renamed_export.json> <out.gs> [--folders]
"""
import json, sys

orig_p, new_p, out_p = sys.argv[1:4]
use_folders = '--folders' in sys.argv
a = json.load(open(orig_p, encoding='utf-8')); a = a.get('containerVersion', a)
b = json.load(open(new_p, encoding='utf-8')); b = b.get('containerVersion', b)

KINDS = (('tag', 'tagId'), ('trigger', 'triggerId'), ('variable', 'variableId'))
ren, dele, folder_of = {}, {}, {}
fname_new = {str(f['folderId']): f['name'] for f in b.get('folder', []) or []}
for k, i in KINDS:
    o = {str(x[i]): x['name'] for x in a.get(k, []) or []}
    n = {str(x[i]): x for x in b.get(k, []) or []}
    ren[k] = {x: [o[x], n[x]['name']] for x in n if x in o and o[x] != n[x]['name']}
    dele[k] = {x: o[x] for x in o if x not in n}
    folder_of[k] = {x: fname_new.get(str(n[x].get('parentFolderId', '')), '') for x in n if x in o}
var_map = {v[0]: v[1] for v in ren['variable'].values()}
tag_map = {v[0]: v[1] for v in ren['tag'].values()}
dele['tag'] = {}  # tags are never deleted

data = {
    'container': (a.get('container') or {}).get('publicId', ''),
    'accountId': str(a.get('accountId', '')), 'containerId': str(a.get('containerId', '')),
    'rename': ren, 'delete': dele, 'varMap': var_map, 'tagMap': tag_map,
    'folders': folder_of if use_folders else {},
}
counts = {k: len(ren[k]) for k, _ in KINDS}
dcounts = {k: len(dele[k]) for k, _ in KINDS}

JS = r'''/**
 * GTM Container Ninja - rename in place (shows as "Modified" in GTM)
 * Container: __CONTAINER__
 * Renames: __COUNTS__   Deletes (not used): __DCOUNTS__
 *
 * HOW TO RUN (about 10 minutes of your time):
 *  1. In GTM, create a NEW workspace (e.g. "Naming review"). Open it and copy the number after
 *     /workspaces/ in the browser address bar. Put it in WORKSPACE_ID below.
 *  2. Go to script.google.com -> New project. Delete the sample code and paste this whole file.
 *  3. Left menu "Services" (+) -> pick "Tag Manager API" -> Add.
 *  4. Leave DRY_RUN = true. Choose the function "run" and click Run. Allow access with your
 *     Google account (the one that can edit this GTM container). Read the log: it lists what
 *     WOULD change, and anything it will skip.
 *  5. Set DRY_RUN = false and click Run again. If the log says "Time limit reached", click Run
 *     again - it carries on where it stopped. Repeat until it says "ALL DONE".
 *  6. In GTM, refresh the workspace: renamed items show as Modified, unused ones as Deleted.
 *     Preview and test as usual. Nothing is published by this script.
 *
 * Safety: an item is only changed when its current name is the expected old name (or already the
 * new name). Anything else is skipped and listed in the log. Only names, {{variable}} references
 * to renamed variables, tag-sequencing names__FOLDERNOTE__ change. Run resetProgress() to start over.
 */
const WORKSPACE_ID = 'PUT_WORKSPACE_NUMBER_HERE';
const DRY_RUN = true;

const DATA = __DATA__;

const T = TagManager.Accounts.Containers.Workspaces;
const PARENT = () => 'accounts/' + DATA.accountId + '/containers/' + DATA.containerId + '/workspaces/' + WORKSPACE_ID;
const START = Date.now();
const LIMIT_MS = 5 * 60 * 1000;

function run() {
  if (!/^\d+$/.test(WORKSPACE_ID)) throw new Error('Put the workspace number in WORKSPACE_ID first.');
  const props = PropertiesService.getScriptProperties();
  const done = DRY_RUN ? {} : JSON.parse(props.getProperty('done') || '{}');
  const log = [];
  const say = (s) => { log.push(s); Logger.log(s); };
  const save = () => { if (!DRY_RUN) props.setProperty('done', JSON.stringify(done)); };
  const outOfTime = () => Date.now() - START > LIMIT_MS;

  const all = {
    variable: listAll_(T.Variables, 'variable'),
    trigger: listAll_(T.Triggers, 'trigger'),
    tag: listAll_(T.Tags, 'tag'),
  };
  const api = { variable: T.Variables, trigger: T.Triggers, tag: T.Tags };
  const idKey = { variable: 'variableId', trigger: 'triggerId', tag: 'tagId' };
  say((DRY_RUN ? 'DRY RUN - nothing is changed. ' : '') + 'Workspace ' + PARENT());

  // 1) update variables, then triggers, then tags: new name + references to renamed variables
  for (const kind of ['variable', 'trigger', 'tag']) {
    for (const item of all[kind]) {
      const id = String(item[idKey[kind]]);
      const key = kind + ':' + id;
      if (done[key]) continue;
      const r = DATA.rename[kind][id];
      let changed = false;
      if (r) {
        if (item.name === r[0]) { item.name = r[1]; changed = true; }
        else if (item.name !== r[1]) { say('SKIP ' + kind + ' ' + id + ': name is "' + item.name + '", expected "' + r[0] + '"'); continue; }
      }
      const before = JSON.stringify(item);
      fixRefs_(item);
      if (JSON.stringify(item) !== before) changed = true;
      if (!changed) continue;
      say((DRY_RUN ? 'WOULD UPDATE ' : 'UPDATE ') + kind + ' ' + id + ': ' + (r ? r[0] + '  ->  ' + r[1] : '(references only) ' + item.name));
      if (!DRY_RUN) { call_(() => api[kind].update(item, item.path, { fingerprint: item.fingerprint })); done[key] = 1; }
      if (outOfTime()) { save(); say('Time limit reached - click Run again to continue.'); return; }
    }
  }

  // 2) delete unused triggers, then unused variables
  for (const kind of ['trigger', 'variable']) {
    const byId = {}; all[kind].forEach(x => byId[String(x[idKey[kind]])] = x);
    for (const id in DATA.delete[kind]) {
      const key = 'del-' + kind + ':' + id;
      if (done[key]) continue;
      const item = byId[id];
      if (!item) { done[key] = 1; continue; }
      if (item.name !== DATA.delete[kind][id]) { say('SKIP delete ' + kind + ' ' + id + ': name is "' + item.name + '"'); continue; }
      say((DRY_RUN ? 'WOULD DELETE ' : 'DELETE ') + kind + ' ' + id + ': ' + item.name);
      if (!DRY_RUN) { call_(() => api[kind].remove(item.path)); done[key] = 1; }
      if (outOfTime()) { save(); say('Time limit reached - click Run again to continue.'); return; }
    }
  }

  // 3) optional: move items into vendor folders
  if (Object.keys(DATA.folders).length && !done['folders']) {
    const folders = {}; (T.Folders.list(PARENT()).folder || []).forEach(f => folders[f.name] = f);
    const want = {};
    for (const kind of ['tag', 'trigger', 'variable']) for (const id in DATA.folders[kind]) {
      const n = DATA.folders[kind][id]; if (!n) continue;
      (want[n] = want[n] || { tagId: [], triggerId: [], variableId: [] })[idKey[kind]].push(id);
    }
    for (const n in want) {
      if (!folders[n]) {
        say((DRY_RUN ? 'WOULD CREATE folder ' : 'CREATE folder ') + n);
        if (!DRY_RUN) folders[n] = call_(() => T.Folders.create({ name: n }, PARENT()));
      }
      say((DRY_RUN ? 'WOULD MOVE ' : 'MOVE ') + (want[n].tagId.length + want[n].triggerId.length + want[n].variableId.length) + ' items to ' + n);
      if (!DRY_RUN) call_(() => T.Folders.move_entities_to_folder({}, folders[n].path, want[n]));
    }
    if (!DRY_RUN) done['folders'] = 1;
  }
  save();
  say(DRY_RUN ? 'DRY RUN finished. Set DRY_RUN = false and run again to apply.' : 'ALL DONE. Refresh the GTM workspace.');
}

function resetProgress() { PropertiesService.getScriptProperties().deleteProperty('done'); }

function listAll_(svc, field) {
  const out = []; let token;
  do {
    const res = call_(() => svc.list(PARENT(), token ? { pageToken: token } : {}));
    (res[field] || []).forEach(x => out.push(x));
    token = res.nextPageToken;
  } while (token);
  return out;
}

function fixRefs_(o) {
  if (Array.isArray(o)) { for (let i = 0; i < o.length; i++) o[i] = fixRefs_(o[i]); return o; }
  if (o && typeof o === 'object') {
    for (const k in o) {
      if (k === 'name' || k === 'path' || k === 'fingerprint') continue;
      if ((k === 'setupTag' || k === 'teardownTag') && Array.isArray(o[k])) {
        o[k].forEach(s => { if (DATA.tagMap[s.tagName]) s.tagName = DATA.tagMap[s.tagName]; });
        continue;
      }
      o[k] = fixRefs_(o[k]);
    }
    return o;
  }
  if (typeof o === 'string' && o.indexOf('{{') >= 0)
    return o.replace(/\{\{([^{}]+)\}\}/g, (m, n) => DATA.varMap[n] ? '{{' + DATA.varMap[n] + '}}' : m);
  return o;
}

function call_(fn) {  // retries when Google says "too many requests"
  for (let i = 0; ; i++) {
    try { const r = fn(); Utilities.sleep(1200); return r; }
    catch (e) {
      if (i < 6 && /429|rate|quota|backend/i.test(String(e))) { Utilities.sleep(5000 * (i + 1)); continue; }
      throw e;
    }
  }
}
'''
js = (JS.replace('__CONTAINER__', data['container'])
        .replace('__COUNTS__', json.dumps(counts)).replace('__DCOUNTS__', json.dumps(dcounts))
        .replace('__FOLDERNOTE__', ' and folders' if use_folders else '')
        .replace('__DATA__', json.dumps(data, ensure_ascii=False, indent=1)))
open(out_p, 'w', encoding='utf-8').write(js)
print(json.dumps({'out': out_p, 'rename': counts, 'delete': dcounts, 'folders': use_folders}))
