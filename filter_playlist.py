import urllib.request
import re
import subprocess
import json

# Sorgente: Tundrak/IPTV-Italia (la lista originale che funzionava)
SOURCE_URL = "https://raw.githubusercontent.com/Tundrak/IPTV-Italia/main/iptvita.m3u"

# ❌ CANALI DA ESCLUDERE (blacklist)
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

# ⏱️ Timeout per ffprobe (secondi). Aumentalo se hai molti canali lenti.
FFPROBE_TIMEOUT = 20

def download_playlist():
    req = urllib.request.Request(SOURCE_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8')

def normalizza(nome):
    nome = nome.lower().strip()
    nome = re.sub(r'\s*\((hd|fhd|4k|sd|uhd)\)\s*$', '', nome)
    nome = re.sub(r'\s+(hd|fhd|4k|sd|uhd)\s*$', '', nome)
    return nome.strip()

def is_channel_alive(url):
    """
    Usa ffprobe per verificare se lo stream è attivo e decodificabile.
    Restituisce True se ffprobe riesce a leggere lo stream, False altrimenti.
    """
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'stream=codec_type',
            '-of', 'json',
            '-timeout', str(FFPROBE_TIMEOUT * 1000000),  # ffprobe usa microsecondi
            url
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=FFPROBE_TIMEOUT + 5  # timeout di sicurezza
        )
        
        # Se ffprobe esce con codice 0, significa che ha letto lo stream
        if result.returncode == 0:
            data = json.loads(result.stdout)
            # Verifica che ci sia almeno uno stream (video o audio)
            return len(data.get('streams', [])) > 0
        return False
        
    except (subprocess.TimeoutExpired, Exception):
        # Timeout o qualsiasi errore -> canale non affidabile
        return False

def filter_channels(content):
    lines = content.splitlines()
    output = ["#EXTM3U"]
    i = 0
    tenuti = []
    esclusi_blacklist = []
    esclusi_morti = []

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

        # 1. Controllo blacklist
        if any(escluso in nome_norm for escluso in CANALI_ESCLUSI):
            esclusi_blacklist.append(nome_canale)
            i += 2
            continue

        # 2. Estrai URL (riga successiva)
        if i + 1 >= len(lines):
            i += 2
            continue
        
        url = lines[i + 1].strip()

        # 3. Controllo se il canale è vivo
        print(f"  Verifico: {nome_canale}...", end=" ")
        if is_channel_alive(url):
            print("OK")
            output.append(line)
            output.append(url)
            tenuti.append(nome_canale)
        else:
            print("MORTO")
            esclusi_morti.append(nome_canale)

        i += 2

    # Log riepilogativo
    print(f"\n=== RIEPILOGO ===")
    print(f"Canali mantenuti: {len(tenuti)}")
    print(f"Esclusi (blacklist): {len(esclusi_blacklist)}")
    print(f"Esclusi (non funzionanti): {len(esclusi_morti)}")
    
    if esclusi_morti:
        print(f"\n--- Canali scartati perché non funzionanti ---")
        for c in esclusi_morti:
            print(f"  ✗ {c}")

    return "\n".join(output)

def main():
    print("Scaricamento playlist sorgente...")
    content = download_playlist()

    print("Filtraggio e verifica canali (potrebbe richiedere alcuni minuti)...")
    filtered = filter_channels(content)

    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(filtered)

    print("\nPlaylist salvata in playlist.m3u")

if __name__ == "__main__":
    main()
