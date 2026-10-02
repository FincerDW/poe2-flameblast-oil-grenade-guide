"""Bundle only game artwork observed in the source guide's nine variants."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import Request, urlopen
from urllib.parse import urlsplit
import hashlib, json, re, mimetypes

ROOT = Path(__file__).parent
OUT = ROOT / 'assets/game'
OUT.mkdir(parents=True, exist_ok=True)
stages = json.loads((ROOT / 'research/source-images.json').read_text(encoding='utf-8'))
sets2 = json.loads((ROOT / 'research/source-gear-set2.json').read_text(encoding='utf-8'))
sources, named, equipment = {}, {}, []

def key(url):
    return url[url.index('/assets/poe-2/images/game/'):].split('?')[0]

def register(im):
    url = im['url']
    if '/assets/poe-2/images/game/' not in url or '/classes/header/' in url:
        return None
    k = key(url)
    if k not in sources or '/cdn-cgi/' not in url:
        sources[k] = url
    return k

for i, stage in enumerate(stages):
    stage_gear, seen = [], set()
    for im in stage['images'] + sets2[i]['images']:
        k = register(im)
        if not k:
            continue
        name = im.get('tooltip') or im.get('context') or ''
        name = re.sub(r'^\d+', '', name)
        name = re.sub(r'Level\s*\d+$', '', name).strip()
        if name and len(name) < 70:
            if name not in named or '/SkillIcons/' in k:
                named[name] = k
        if im.get('alt') == 'item' and k not in seen:
            stage_gear.append(k)
            seen.add(k)
    equipment.append(stage_gear)

named['Morior Invictus'] = named['Morior Invictus (life)']
for k in sources:
    if k.endswith('/GoldRing.webp'): named['Gold Ring'] = k

def download(pair):
    k, url = pair
    filename = hashlib.sha256(k.encode()).hexdigest()[:10] + '-' + Path(k).name
    path = OUT / filename
    if not path.exists():
        last = None
        for attempt in range(3):
            try:
                with urlopen(Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=40) as response:
                    data = response.read()
                    mime = response.headers.get_content_type()
                if not mime.startswith('image/') and not (data[:4] in [b'RIFF',b'\x89PNG'] or data[:2] == b'\xff\xd8' or (data[4:8] == b'ftyp' and data[8:12] in [b'avif',b'avis'])):
                    raise ValueError(f'Expected image, got {mime}: {url}')
                path.write_bytes(data)
                break
            except Exception as exc:
                last = exc
        else:
            raise last
    signature = path.read_bytes()[:12]
    mime = 'image/webp' if signature[:4] == b'RIFF' else 'image/png' if signature[:4] == b'\x89PNG' else 'image/jpeg' if signature[:2] == b'\xff\xd8' else mimetypes.guess_type(filename)[0]
    return k, {'path':path.relative_to(ROOT).as_posix(), 'url':url, 'mime':mime, 'bytes':path.stat().st_size}

assets = {}
with ThreadPoolExecutor(max_workers=8) as pool:
    for future in as_completed([pool.submit(download, pair) for pair in sources.items()]):
        k, result = future.result()
        assets[k] = result
        if len(assets) % 20 == 0: print(f'Downloaded {len(assets)}/{len(sources)}',flush=True)
manifest = {'source':'https://mobalytics.gg/poe-2/builds/fubgun-flameblast-oil-grenade', 'assets':assets, 'names':named, 'equipment':equipment}
(ROOT / 'research/asset-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'{len(assets)} images; {len(named)} named entries; {sum(a["bytes"] for a in assets.values()):,} bytes')
