import urllib.request
import re

# Sorgente: playlist IPTV-org per l'Italia
SOURCE_URL = "https://iptv-org.github.io/iptv/countries/it.m3u"

# ✅ CANALI RAI (gruppo separato)
CANALI_RAI = [
    "rai 1", "rai 2", "rai 3", "rai 4", "rai 5",
    "rai movie", "rai premium", "rai gulp", "rai yoyo",
    "rai news 24", "rai storia", "rai scuola", "rai sport",
]

# ✅ CANALI MEDIASET (gruppo separato)
CANALI_MEDIASET = [
    "rete 4", "canale 5", "italia 1", "italia 2",
    "20 mediaset", "iris", "la 5", "cine34", "focus",
    "top crime", "boing", "cartoonito", "mediaset extra",
    "tgcom 24", "twenty seven",
]

# ✅ ALTRI CANALI - mappa nome -> categoria
CANALI_ALTRI = {
    # Generalista
    "la7": "Generalista",
    "la7d": "Generalista",
    "tv8": "Generalista",
    "cielo": "Generalista",
    "nove": "Generalista",
    "super!": "Generalista",

    # Film
    "cine34": "Film",
    "iris": "Film",
    "twenty seven": "Film",
    "rai movie": "Film",

    # Ragazzi
    "k2": "Ragazzi",
    "frisbee": "Ragazzi",
    "boing": "Ragazzi",
    "cartoonito": "Ragazzi",
    "rai gulp": "Ragazzi",
    "rai yoyo": "Ragazzi",
    "super!": "Ragazzi",

    # News
    "sky tg24": "News",
    "tgcom 24": "News",
    "rai news 24": "News",

    # Sport
    "sportitalia": "Sport",
    "supertennis": "Sport",
    "rai sport": "Sport",

    # Discovery / Factual
    "real time": "Discovery",
    "food network": "Discovery",
    "dmax": "Discovery",
    "motor trend": "Discovery",
    "giallo": "Discovery",
    "warner tv": "Discovery",
    "hgtv": "Discovery",
    "focus": "Discovery",
    "top crime": "Discovery",
}

# ❌ CANALI DA ESCLUDERE (blacklist) - priorità su tutto
CANALI_ESCLUSI = [
    # Radio
    "radio", "rds", "rtl", "deejay", "m2o", "virgin",
    "kiss kiss", "105", "capital", "montecarlo", "zeta",
    "freccia", "r101",
    # Religione
    "padre pio", "tv2000", "telepace", "santuario",
    "maria", "cristo", "vaticano", "chiesa", "fede",
    "religione", "gospel", "speranza",
    # Shopping
    "qvc", "hse", "home shopping", "shop", "teleshopping",
    "gioielli", "moda", "bellezza", "vendita",
    # Musica
    "mtv", "vh1", "deejay tv", "music", "musica",
    "kiss", "radio italia", "rds social",
    # Cultura
    "arte", "cultura", "documentari", "museo", "teatro", "opera",
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

def appartiene_a(nome_norm, lista):
    return any(voce in nome_norm for voce in lista)

def trova_categoria_altri(nome_norm):
    """Cerca la categoria per un canale 'Altri'. Ritorna None se non trovato."""
    # Cerca la corrispondenza più lunga (per evitare match parziali errati)
    miglior_match = None
    miglior_lunghezza = 0
    for chiave, categoria in CANALI_ALTRI.items():
        if chiave in nome_norm and len(chiave) > miglior_lunghezza:
            miglior_match = categoria
            miglior_lunghezza = len(chiave)
    return miglior_match

def filter_channels(content):
    lines = content.splitlines()
    output = ["#EXTM3U"]
    i = 0
    tenuti = {}  # categoria -> lista canali

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

        # Escludi se è nella blacklist (priorità assoluta)
        if appartiene_a(nome_norm, CANALI_ESCLUSI):
            i += 2
            continue

        # Determina il gruppo
        gruppo = None
        if appartiene_a(nome_norm, CANALI_RAI):
            gruppo = "Rai"
        elif appartiene_a(nome_norm, CANALI_MEDIASET):
            gruppo = "Mediaset"
        else:
            gruppo = trova_categoria_altri(nome_norm)

        if gruppo is None:
            i += 2
            continue

        # Riscrivi la riga #EXTINF con il group-title corretto
        nuova_linea = re.sub(
            r'group-title="[^"]*"',
            f'group-title="{gruppo}"',
            line
        )
        if 'group-title=' not in nuova_linea:
            nuova_linea = nuova_linea.replace(
                '#EXTINF:-1',
                f'#EXTINF:-1 group-title="{gruppo}"'
            )

        output.append(nuova_linea)
        if i + 1 < len(lines):
            output.append(lines[i + 1].strip())

        tenuti.setdefault(gruppo, []).append(nome_canale)
        i += 2

    # Log riepilogativo
    for gruppo in sorted(tenuti.keys()):
        canali = tenuti[gruppo]
        print(f"\n=== {gruppo} ({len(canali)} canali) ===")
        for c in canali:
            print(f"  ✓ {c}")

    totale = sum(len(v) for v in tenuti.values())
    print(f"\nTotale canali mantenuti: {totale}")

    return "\n".join(output)

def main():
    print("Scaricamento playlist sorgente...")
    content = download_playlist()

    print("Filtraggio canali...")
    filtered = filter_channels(content)

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(filtered)

    print("\nPlaylist salvata in playlist.m3u")

if __name__ == "__main__":
    main()
