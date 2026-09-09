#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tc-immagini.py — il ciclo completo delle foto del sito.

  python3 tc-immagini.py scarica     copia di sicurezza: tira giu tutte le foto
                                     dal vecchio sito in originali/<progetto>/,
                                     piu quelle non pubblicate in _archivio-cdn/
  python3 tc-immagini.py stato       a che punto siamo, progetto per progetto
  python3 tc-immagini.py provino     per ogni cartella dentro originali/ crea una
                                     tavola numerata in provini/, da mandare a Tommy
  python3 tc-immagini.py prepara     legge selezione.txt, scrive img/<progetto>/
                                     e aggiorna index.html da solo

COME SI LAVORA
Le foto che manda Tommy si mettono in originali/<nomeprogetto>/, una cartella per
progetto. Il nome della cartella e' quello che si usera' anche in selezione.txt.
Le cartelle possono nascere da 'scarica' oppure essere create a mano con il
materiale nuovo che arriva da lui. Per il programma non cambia niente.

'provino' scrive dentro ogni cartella un file elenco.txt che congela la
numerazione. Da quel momento i numeri non cambiano piu' anche se si aggiungono
file: i nuovi vanno in coda. Serve perche' Tommy risponde con i numeri.
Se una cartella cambia molto e si vuole ripartire, si cancella il suo elenco.txt.

selezione.txt: una riga per progetto, numeri presi dal provino,
nell'ordine in cui devono apparire.

Modo semplice, con la misura accanto:
G grande, tutta la riga. M media, mezza riga. P piccola, un terzo.
Senza lettera vale M.

  holden: 4G, 1M, 7M, 12P, 9P, 3P

Modo libero, per riprodurre un'impaginazione disegnata da Tommy.
Dopo il numero si scrive uguale e poi la posizione, su dodici colonne:
larghezza, chiocciola e colonna di partenza, cappello e scarto verticale.

  patty: 4=3@2, 2=3@6^70, 3=3@4^60, 1=3@8, 6=5@5^40

  4=3@2      larga 3 colonne su 12, parte dalla colonna 2
  2=3@6^70   larga 3, parte dalla 6, abbassata di 70 pixel
  6=5@5^-40  larga 5, parte dalla 5, alzata di 40 pixel

I due modi si possono mescolare nella stessa riga.

Serve index.html nella stessa cartella per 'scarica' e per i nomi dei progetti.
"""
import os, re, io, json, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, 'index.html')
ORIG = os.path.join(HERE, 'originali')
PROV = os.path.join(HERE, 'provini')
OUT = os.path.join(HERE, 'img')
SEL = os.path.join(HERE, 'selezione.txt')
INV = os.path.join(HERE, 'TC-inventario-unico.tsv')

# lato lungo di pubblicazione, diverso per misura: una piccola non serve grande
LATI = {'L': 2000, 'M': 1400, 'S': 900}
QUALITA = 82
BUONE = ('.jpg', '.jpeg', '.png', '.tif', '.tiff', '.webp')

def progetti():
    if not os.path.exists(INDEX):
        return []
    src = io.open(INDEX, encoding='utf-8').read()
    m = re.search(r'const P = (\[.*?\]);\n', src, re.S)
    return json.loads(m.group(1)) if m else []

def solo_nome(u):
    return str(u).split('|')[0]

def cartelle():
    if not os.path.isdir(ORIG):
        return []
    return sorted(d for d in os.listdir(ORIG) if os.path.isdir(os.path.join(ORIG, d)))

def elenco_di(pid):
    """Numerazione congelata della cartella. Se non c'e' la crea in ordine di nome."""
    d = os.path.join(ORIG, pid)
    man = os.path.join(d, 'elenco.txt')
    presenti = sorted(f for f in os.listdir(d) if f.lower().endswith(BUONE))
    if os.path.exists(man):
        vecchi = [r.strip() for r in io.open(man, encoding='utf-8') if r.strip()]
        vecchi = [f for f in vecchi if f in presenti]
        ordine = vecchi + [f for f in presenti if f not in vecchi]
    else:
        ordine = presenti
    io.open(man, 'w', encoding='utf-8').write('\n'.join(ordine))
    scartati = [f for f in os.listdir(d)
                if not f.lower().endswith(BUONE) and f != 'elenco.txt' and not f.startswith('.')]
    return ordine, scartati

# ---------------------------------------------------------------- scarica
def scarica():
    tot = 0
    for p in progetti():
        urls = p.get('i') or []
        if not urls:
            continue
        d = os.path.join(ORIG, p['id'])
        os.makedirs(d, exist_ok=True)
        for k, u in enumerate(urls, 1):
            u = solo_nome(u)
            if not u.startswith('http'):
                continue
            nome = '%03d_%s' % (k, u.rsplit('/', 1)[-1].split('_', 1)[-1])
            dst = os.path.join(d, nome)
            if os.path.exists(dst) and os.path.getsize(dst) > 1000:
                continue
            try:
                req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
                data = urllib.request.urlopen(req, timeout=45).read()
                open(dst, 'wb').write(data)
                tot += 1
                print('  %s / %s  %d kB' % (p['id'], nome, len(data) // 1024))
                time.sleep(0.25)
            except Exception as e:
                print('  MANCA %s / %s  (%s)' % (p['id'], nome, e))
    tot += scarica_non_pubblicate()
    print('\nScaricate %d foto in %s' % (tot, ORIG))

def scarica_non_pubblicate():
    """Le immagini presenti sul CDN ma non pubblicate sul sito, se abbiamo l'indirizzo.
    Finiscono tutte in originali/_archivio-cdn/, sono materiale da valutare."""
    if not os.path.exists(INV):
        return 0
    import csv
    d = os.path.join(ORIG, '_archivio-cdn')
    os.makedirs(d, exist_ok=True)
    tot = 0
    for r in csv.DictReader(io.open(INV, encoding='utf-8'), delimiter='\t'):
        u = (r.get('url_grande') or '').strip()
        if not u or r.get('pubblicata_nel_sito') == 'si':
            continue
        dst = os.path.join(d, r['file'])
        if os.path.exists(dst) and os.path.getsize(dst) > 1000:
            continue
        try:
            req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
            open(dst, 'wb').write(urllib.request.urlopen(req, timeout=45).read())
            tot += 1
            print('  _archivio-cdn / %s' % r['file'])
            time.sleep(0.25)
        except Exception as e:
            print('  MANCA _archivio-cdn / %s  (%s)' % (r['file'], e))
    return tot

# ---------------------------------------------------------------- stato
def stato():
    scelte = leggi_selezione() if os.path.exists(SEL) else {}
    nel_sito = {p['id']: p['n'] for p in progetti()}
    print('%-14s %6s %9s %8s  %s' % ('cartella', 'foto', 'provino', 'scelte', 'nel sito'))
    for pid in cartelle():
        files, scartati = elenco_di(pid)
        pv = 'si' if os.path.exists(os.path.join(PROV, pid + '.jpg')) else 'no'
        sc = len(scelte.get(pid, [])) or '-'
        print('%-14s %6d %9s %8s  %s' % (pid, len(files), pv, sc, nel_sito.get(pid, 'DA AGGIUNGERE')))
        if scartati:
            print('               da convertire: %s' % ', '.join(scartati[:6]))
    mancanti = [i for i in nel_sito if i not in cartelle()]
    if mancanti:
        print('\nNel sito ma senza cartella locale: %s' % ', '.join(mancanti))

# ---------------------------------------------------------------- provino
def provino():
    from PIL import Image, ImageDraw, ImageFont
    COL, CELLA, MARG, PIE, TESTA = 4, 460, 40, 54, 96
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 26)
        fbig = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 34)
    except Exception:
        font = fbig = ImageFont.load_default()
    os.makedirs(PROV, exist_ok=True)
    nomi = {p['id']: p['n'] for p in progetti()}
    for pid in cartelle():
        files, scartati = elenco_di(pid)
        if not files:
            continue
        righe = (len(files) + COL - 1) // COL
        W = MARG * 2 + COL * CELLA
        H = MARG * 2 + TESTA + righe * (CELLA + PIE)
        sheet = Image.new('RGB', (W, H), 'white')
        dr = ImageDraw.Draw(sheet)
        dr.text((MARG, MARG), '%s  ·  %d foto' % (nomi.get(pid, pid), len(files)), fill='black', font=fbig)
        dr.text((MARG, MARG + 42), 'numero + misura:  G grande, M media, P piccola',
                fill='#8a8a8a', font=font)
        for k, f in enumerate(files):
            try:
                im = Image.open(os.path.join(ORIG, pid, f)).convert('RGB')
            except Exception as e:
                print('  non riesco ad aprire %s/%s (%s)' % (pid, f, e))
                continue
            im.thumbnail((CELLA - 20, CELLA - 20))
            x = MARG + (k % COL) * CELLA
            y = MARG + TESTA + (k // COL) * (CELLA + PIE)
            sheet.paste(im, (x + (CELLA - 20 - im.width) // 2, y + (CELLA - 20 - im.height) // 2))
            dr.text((x + 4, y + CELLA - 16), str(k + 1), fill='#c1362a', font=fbig)
        sheet.save(os.path.join(PROV, '%s.jpg' % pid), quality=88, optimize=True)
        print('  provini/%s.jpg  (%d foto)' % (pid, len(files)))
        if scartati:
            print('     fuori dalla tavola, formato non gestito: %s' % ', '.join(scartati[:6]))
    print('\nProvini pronti in %s' % PROV)

# ---------------------------------------------------------------- prepara
MIS = {'G': 'L', 'L': 'L', 'M': 'M', 'P': 'S', 'S': 'S'}

def leggi_selezione():
    """Ogni voce e (numero, misura). La misura e una lettera oppure una
    posizione libera del tipo 3@6^70."""
    scelte = {}
    for riga in io.open(SEL, encoding='utf-8'):
        riga = riga.split('#')[0].strip()
        if not riga or ':' not in riga:
            continue
        pid, resto = riga.split(':', 1)
        voci = []
        for pezzo in resto.split(','):
            pezzo = pezzo.strip()
            if not pezzo:
                continue
            m = re.match(r'^(\d+)\s*(?:=\s*(\d{1,2}(?:@\d{1,2})?(?:\^-?\d{1,3})?)|([A-Za-z]))?$', pezzo)
            if not m:
                print('  riga non capita: %s' % pezzo)
                continue
            n = int(m.group(1))
            if m.group(2):
                voci.append((n, m.group(2)))
            else:
                voci.append((n, MIS.get((m.group(3) or 'M').upper(), 'M')))
        if voci:
            scelte[pid.strip()] = voci
    return scelte

def lato_di(mis):
    """Quanto grande va salvata la foto: dipende da quanto spazio occupa."""
    if mis in LATI:
        return LATI[mis]
    n = int(re.match(r'^(\d{1,2})', mis).group(1))
    return 2000 if n >= 9 else (1400 if n >= 5 else 900)

def prepara():
    from PIL import Image
    if not os.path.exists(SEL):
        sys.exit('Manca selezione.txt')
    blocchi, peso = {}, 0
    for pid, voci in leggi_selezione().items():
        d = os.path.join(ORIG, pid)
        if not os.path.isdir(d):
            print('  %s: cartella non trovata' % pid)
            continue
        files, _ = elenco_di(pid)
        dst = os.path.join(OUT, pid)
        os.makedirs(dst, exist_ok=True)
        elenco = []
        for pos, (n, mis) in enumerate(voci, 1):
            if n < 1 or n > len(files):
                print('  %s: il numero %d non esiste, ce ne sono %d' % (pid, n, len(files)))
                continue
            im = Image.open(os.path.join(d, files[n - 1])).convert('RGB')
            lato = lato_di(mis)
            if max(im.size) > lato:
                r = lato / max(im.size)
                im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
            nome = '%02d.jpg' % pos
            f = os.path.join(dst, nome)
            im.save(f, quality=QUALITA, optimize=True, progressive=True)
            peso += os.path.getsize(f)
            elenco.append('img/%s/%s|%s' % (pid, nome, mis))
        blocchi[pid] = elenco
        print('  %s: %d foto pronte' % (pid, len(elenco)))
    io.open(os.path.join(HERE, 'nuovi-elenchi.json'), 'w', encoding='utf-8').write(
        json.dumps(blocchi, indent=1, ensure_ascii=False))
    print('\nTotale %.1f MB.' % (peso / 1048576))
    aggiorna_index(blocchi)

def aggiorna_index(blocchi):
    """Riscrive index.html sostituendo gli elenchi dei progetti toccati.
    Prima salva una copia di sicurezza, cosi si puo sempre tornare indietro."""
    if not os.path.exists(INDEX):
        print('index.html non trovato, non aggiorno niente'); return
    src = io.open(INDEX, encoding='utf-8').read()
    m = re.search(r'const P = (\[.*?\]);\n', src, re.S)
    if not m:
        print('non trovo l elenco dei progetti dentro index.html'); return
    P = json.loads(m.group(1))
    noti = {p['id'] for p in P}
    cambiati = []
    for pid, elenco in blocchi.items():
        if pid not in noti:
            print('  %s non esiste ancora in index.html, va aggiunto a mano' % pid); continue
        for p in P:
            if p['id'] == pid:
                p['i'] = elenco; cambiati.append(pid)
    if not cambiati:
        return
    io.open(INDEX + '.backup', 'w', encoding='utf-8').write(src)
    nuovo = src[:m.start(1)] + json.dumps(P, ensure_ascii=False) + src[m.end(1):]
    io.open(INDEX, 'w', encoding='utf-8').write(nuovo)
    print('index.html aggiornato: %s' % ', '.join(cambiati))
    print('copia di sicurezza in index.html.backup')

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    {'scarica': scarica, 'stato': stato, 'provino': provino, 'prepara': prepara}.get(
        cmd, lambda: sys.exit(__doc__))()
