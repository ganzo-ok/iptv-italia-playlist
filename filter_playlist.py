import urllib.request
import re

# Sorgente: playlist IPTV-org per l'Italia (mantenuta attivamente)
SOURCE_URL = "https://iptv-org.github.io/iptv/countries/it.m3u"

# Parole chiave che indicano canali radio (da escludere)
RADIO_KEYWORDS = [
    "radio", "rds", "rtl", "deejay", "m2o", "virgin", 
    "kiss kiss", "105", "capital", "montecarlo", "zeta", 
    "freccia", "r101", "serie a"
]

# Canali per ragazzi da mantenere esplicitamente
KIDS_CHANNELS = [
    "rai yoyo", "rai gulp", "boing", "cartoonito", 
    "k2", "frisbee", "super!", "italia 2"
]

def download_playlist():
    req = urllib.request.Request(SOURCE_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8')

def filter_channels(content):
    lines = content.splitlines()
    output = ["#EXTM3U"]
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Mantieni righe vuote o commenti generici
        if not line.startswith("#EXTINF"):
            if line and not line.startswith("#"):
                output.append(line)
            i += 1
            continue
        
        # Estrai il nome del canale dalla riga #EXTINF
        # Formato: #EXTINF:-1 ...,Nome Canale
        match = re.search(r',(.+)$', line)
        if not match:
            i += 1
            continue
        
        channel_name = match.group(1).lower()
        
        # Verifica se è un canale radio
        is_radio = any(keyword in channel_name for keyword in RADIO_KEYWORDS)
        
        # Verifica se è un canale per ragazzi
        is_kids = any(kids in channel_name for kids in KIDS_CHANNELS)
        
        # Salta le radio (ma mantieni i canali per ragazzi)
        if is_radio and not is_kids:
            # Salta questa riga e la prossima (URL)
            i += 2
            continue
        
        # Aggiungi la riga #EXTINF e la successiva (URL)
        output.append(line)
        if i + 1 < len(lines):
            output.append(lines[i + 1].strip())
        i += 2
    
    return "\n".join(output)

def main():
    print("Scaricamento playlist sorgente...")
    content = download_playlist()
    
    print("Filtraggio canali radio...")
    filtered = filter_channels(content)
    
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write(filtered)
    
    print("Playlist filtrata salvata in playlist.m3u")

if __name__ == "__main__":
    main()