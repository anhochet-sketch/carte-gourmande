#!/bin/bash
#
# 🍯 CARTE GOURMANDE — Correction ciblée des 17 images (version racine)
# ──────────────────────────────────────────────────────────────────────
# Adapté à ton organisation : les images sont à la racine du dépôt.
#

set -e
echo "🍯 Carte Gourmande — Correction ciblée"
echo "======================================="

if [ ! -f "data.js" ]; then
  echo "❌ data.js manquant dans le dossier courant"; exit 1
fi

python3 -c "import PIL" 2>/dev/null || pip3 install --user Pillow --quiet

cat > _correct_images.py << 'PYEOF'
import json, re, os, time, unicodedata
import urllib.request, urllib.parse
import ssl
from PIL import Image
from io import BytesIO

# Liste ciblée : nom du site → mot-clé de contexte
TARGETS = {
    "Beaufort": "fromage",
    "Comté": "fromage",
    "Fleur de sel d'Aigues-Mortes": "sel",
    "Langres": "fromage",
    "Livarot": "fromage",
    "Mont d'Or": "fromage vacherin",
    "Moutarde de Dijon": "moutarde condiment",
    "Munster": "fromage",
    "Mâconnais": "fromage chèvre",
    "Navettes de Marseille": "biscuit pâtisserie",
    "Pouligny-Saint-Pierre": "fromage chèvre",
    "Pâte de fruits de Saint-Didier": "pâte de fruits confiserie",
    "Saint-Maure-de-Touraine": "fromage chèvre",
    "Saint-Nectaire": "fromage",
    "Selles-sur-Cher": "fromage chèvre",
    "Valençay": "fromage chèvre",
    "Époisses": "fromage",
}

with open('data.js', 'r', encoding='utf-8') as f:
    content = f.read()
m = re.search(r'window\.FULL_DATA\s*=\s*(\[.*\]);?\s*$', content, re.DOTALL)
data = json.loads(m.group(1))

ctx = ssl.create_default_context()
UA = 'CarteGourmande/1.0 (https://carte-gourmande.pages.dev)'

def slugify(name):
    n = unicodedata.normalize('NFKD', name)
    n = ''.join(c for c in n if not unicodedata.combining(c))
    n = re.sub(r'[^\w\s-]', '', n).strip().lower()
    return re.sub(r'[-\s]+', '-', n)

def smart_encode_url(url):
    parts = urllib.parse.urlsplit(url)
    path = urllib.parse.quote(parts.path, safe="/%:@!$&'()*+,;=-._~")
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))

def http_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        return json.loads(resp.read())

def search_commons(query):
    """Cherche une image sur Wikimedia Commons en filtrant les images de villages."""
    try:
        api = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search&srsearch={urllib.parse.quote(query)}&srnamespace=6&srlimit=8"
        d = http_json(api)
        for r in d.get('query', {}).get('search', []):
            title = r['title']
            if not any(title.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                continue
            title_lower = title.lower()
            # Filtres anti-village/lieu
            skip_keywords = ['village', 'commune', 'mairie', 'church', 'eglise', 'église',
                            'aerial', 'aerienne', 'aérienne', 'panorama', 'view', 'vue_generale',
                            'centre_bourg', 'place_de', 'rue_principale', 'paysage', 'landscape',
                            'townhall', 'monument', 'castle', 'château_de']
            if any(kw in title_lower for kw in skip_keywords):
                continue
            api2 = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url&titles={urllib.parse.quote(title)}"
            d2 = http_json(api2)
            for page_id, info in d2.get('query', {}).get('pages', {}).items():
                if 'imageinfo' in info:
                    return info['imageinfo'][0]['url']
        return None
    except Exception as e:
        return None

def download_and_save(url, filename):
    """Sauvegarde DANS LE DOSSIER COURANT (racine), pas dans images/."""
    out = filename  # racine
    try:
        url_clean = smart_encode_url(url)
        req = urllib.request.Request(url_clean, headers={
            'User-Agent': UA,
            'Accept': 'image/*,*/*',
            'Referer': 'https://carte-gourmande.pages.dev/',
        })
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            img_data = resp.read()
        img = Image.open(BytesIO(img_data))
        if img.mode in ('RGBA', 'LA', 'P'):
            bg = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P': img = img.convert('RGBA')
            bg.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        if img.width > 800:
            ratio = 800 / img.width
            img = img.resize((800, int(img.height * ratio)), Image.LANCZOS)
        img.save(out, 'JPEG', quality=82, optimize=True, progressive=True)
        return True
    except Exception as e:
        return False

# Supprimer d'abord les anciennes images dans le dossier courant (RACINE)
print(f"🗑️  Suppression des {len(TARGETS)} anciennes images...")
for name in TARGETS.keys():
    slug = slugify(name)
    fpath = f"{slug}.jpg"  # racine, pas images/
    if os.path.exists(fpath):
        os.remove(fpath)
        print(f"   - supprimée : {fpath}")

print(f"\n🔍 Recherche contextualisée et téléchargement...")
ok_count = 0
fail = []

for i, (name, context_word) in enumerate(TARGETS.items()):
    slug = slugify(name)
    queries = [
        f"{name} {context_word}",
        f"{name.split(' ')[0]} {context_word}",
        f"{context_word} {name.split(' ')[0]}",
    ]
    queries = list(dict.fromkeys(queries))
    
    found = False
    print(f"\n[{i+1}/{len(TARGETS)}] {name}")
    for q in queries:
        print(f"   Recherche : « {q} »", end=' ', flush=True)
        url = search_commons(q)
        if url:
            filename = url.split('/')[-1][:60]
            print(f"→ {filename}")
            if download_and_save(url, f"{slug}.jpg"):
                ok_count += 1
                # Mettre à jour data.js avec chemin RACINE
                for item in data:
                    if item['name'] == name:
                        item['image'] = f"{slug}.jpg"  # racine
                found = True
                break
            else:
                print(f"   ⚠️  Téléchargement échoué, on essaie autre chose")
        else:
            print("→ rien trouvé")
        time.sleep(0.5)
    
    if not found:
        fail.append(name)
        print(f"   ❌ Aucune bonne image trouvée pour {name}")
    
    time.sleep(0.4)

# Sauver data.js
with open('data.js', 'w', encoding='utf-8') as f:
    f.write("window.FULL_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n")

print(f"\n" + "="*50)
print(f"✅ {ok_count}/{len(TARGETS)} images corrigées")
print(f"📁 data.js mis à jour")
if fail:
    print(f"\n⚠️  Toujours sans bonne image automatique : {fail}")
    print("   → on les traitera à la main si besoin")

# Lister les fichiers à uploader
print(f"\n📤 Fichiers à uploader sur GitHub :")
print(f"   - data.js")
created_files = []
for name in TARGETS.keys():
    slug = slugify(name)
    if os.path.exists(f"{slug}.jpg"):
        created_files.append(f"{slug}.jpg")
for f in created_files:
    print(f"   - {f}")
PYEOF

python3 _correct_images.py
rm _correct_images.py

echo ""
echo "🎉 Terminé !"
