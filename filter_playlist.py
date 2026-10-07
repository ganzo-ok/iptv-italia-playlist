import urllib.request
import re

# Sorgente: Tundrak/IPTV-Italia (la lista originale che funzionava)
SOURCE_URL = "https://raw.githubusercontent.com/Tundrak/IPTV-Italia/main/iptvita.m3u"

# ❌ CANALI DA ESCLUDERE (blacklist) - aggiungi qui quello che NON vuoi
# Il confronto è "contiene", quindi "radio" esclude "Radio 105", "Radio Italia", ecc.
CANALI_ESCLUSI = [
    # Radio
    "radio", "rds", "rtl", "deejay", "m2o", "virgin",
    "kiss kiss", "105", "capital", "montecarlo", "zeta",
    "freccia", "r101", "rtl 102.5",

    # Religione
    "padre pio", "tv2000", "telepace", "santuario",
    "maria", "cristo", "vaticano", "chiesa", "fede",
    "religione", "gospel", "speranza",

    # Shopping
    "qvc", "hse", "home shopping", "shop", "teleshopping",
    "gioielli", "moda", "bellezza", "vendita",

    # Musica
    "mtv", "vh1", "music", "musica",
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
    esclusi = []

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

        # Escludi se contiene una delle parole della blacklist
        if any(escluso in nome_norm for escluso in CANALI_ESCLUSI):
            esclusi.append(nome_canale)
            i += 2
            continue

        output.append(line)
        if i + 1 < len(lines):
            output.append(lines[i + 1].strip())
        tenuti.append(nome_canale)

        i += 2

    print(f"Canali mantenuti: {len(tenuti)}")
    print(f"Canali esclusi: {len(esclusi)}")
    print("\n--- Mantenuti ---")
    for c in tenuti:
        print(f"  ✓ {c}")
    print("\n--- Esclusi ---")
    for c in esclusi:
        print(f"  ✗ {c}")

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
