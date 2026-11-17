import csv, io, json, re, sys, zipfile
# signature technique per dex, read as text from the site's app.min.js (argv[3])
js = open(sys.argv[3], encoding='utf-8').read()
tech = {int(m[1]): re.sub(r'\\(.)', r'\1', m[2] if m[2] is not None else m[3]) for m in re.finditer(
    r'\{dex:(\d+),name:"[^"]*"[^{}]*?tech:\[(?:"((?:[^"\\]|\\.)*)"|\'((?:[^\'\\]|\\.)*)\')', js)}
z = zipfile.ZipFile(sys.argv[1])
fr = json.loads(z.read('frames.json'))['creatures']
rows = {r['dex']: r for r in csv.DictReader(io.TextIOWrapper(z.open('index.csv'), 'utf-8'))}
out = []
for dex, c in fr.items():
    r = rows[dex]
    f = {k: [v['x'], v['y'], v['w'], v['h'], v['anchorX'], v['anchorY']] for k, v in c['frames'].items()}
    out.append({'id': int(dex), 'n': c['name'], 'st': c['stage'], 't': r['types'].split('/')[0] or 'normal',
                'a': r['attribute'], 'fly': c['fly'], 'sz': c['sizeClass'], 's': c['sheet'], 'f': f, 'u': tech[int(dex)]})
assert len(out) == 436 and tech[1] == 'Baby Flame' and all('map' in o['f'] or 'battle' in o['f'] for o in out)
open(sys.argv[2], 'w', encoding='utf-8').write('window.ROSTER=' + json.dumps(out, separators=(',', ':')) + ';\n')
print(len(out), sum('map' not in o['f'] for o in out), 'missing map')
