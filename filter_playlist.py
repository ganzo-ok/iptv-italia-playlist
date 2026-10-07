import urllib.request
import re

# Sorgente: playlist IPTV-org per l'Italia (mantenuta attivamente)
SOURCE_URL = "https://iptv-org.github.io/iptv/countries/it.m3u"

# ✅ CANALI DA TENERE (whitelist)
CANALI_DESIDERATI = [
    # Rai
    "rai 1", "rai 2", "rai 3", "rai 4", "rai 5",
    "rai movie", "rai premium", "rai gulp", "rai yoyo",
    "rai news 24", "rai storia", "rai scuola", "rai sport",

    # Mediaset
    "rete 4", "canale 5", "italia 1", "italia 2",
    "20 mediaset", "iris", "la 5", "cine34", "focus",
    "top crime", "boing", "cartoonito", "mediaset extra",
    "tgcom 24", "twenty seven",

    # Discovery / Warner
    "nove", "real time", "food network", "k2", "frisbee",
    "dmax", "motor trend", "giallo", "warner tv", "hgtv",

    # Altri
    "la7", "la7d", "tv8", "cielo", "sky tg24", "tv2000",
    "qvc", "super!", "sportitalia", "supertennis",

    # Film
    "rai movie", "cine34", "iris", "twenty seven",
]

# ❌ CANALI DA ESCLUDERE (blacklist) - priorità sulla whitelist
CANALI_ESCLUSI = [
    "radio", "rds", "rtl", "deejay", "m2o", "virgin",
    "kiss kiss", "105", "capital", "montecarlo", "zeta",
    "freccia", "r101",
]

def download_playlist():
    req = urllib.request.Request(SOURCE_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8')

def normalizza(nome):
    """Rimuove suffissi HD/FHD/4K e spazi extra per il confronto."""
    nome = nome.lower().strip()
    nome = re.sub(r'\s*\((hd|fhd|4k|sd|uhd)\)\s*$', '', nome)
    nome = re.sub(r'\s+(hd|fhd|4k|sd|uhd)\s*$', '', nome)
    return nome.strip()

def filter_channels(content):
    lines = content.splitlines()
    output = ["#EXTM3U"]
    i = 0
    tenuti = []

    while i < len(lines):
        line = lines[i].strip()

        if not line.startswith("#EXTINF"):
            i += 1
            continue

        match = re.search(r',(.+)$', line)
        if not match:
            i += 1
            continue

        nome_canale = match.group(1)
        nome_norm = normalizza(nome_canale)

        # Escludi se è nella blacklist
        if any(escluso in nome_norm for escluso in CANALI_ESCLUSI):
            i += 2
            continue

        # Tieni solo se è nella whitelist
        if any(desiderato in nome_norm for desiderato in CANALI_DESIDERATI):
            output.append(line)
            if i + 1 < len(lines):
                output.append(lines[i + 1].strip())
            tenuti.append(nome_canale)

        i += 2

    print(f"Canali mantenuti: {len(tenuti)}")
    for c in tenuti:
        print(f"  ✓ {c}")

    return "\n".join(output)

def main():
    print("Scaricamento playlist sorgente...")
    content = download_playlist()

    print("Filtraggio canali...")
    filtered = filter_channels(content)

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(filtered)

    print("Playlist salvata in playlist.m3u")

if __name__ == "__main__":
    main()
