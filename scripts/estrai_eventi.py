#!/usr/bin/env python3
import json,re,sys,unicodedata
from pathlib import Path
import fitz
PDF=Path(sys.argv[1]); OUT=Path(sys.argv[2])
MONTH='GENNAIO|FEBBRAIO|MARZO|APRILE|MAGGIO|GIUGNO|LUGLIO|AGOSTO|SETTEMBRE|OTTOBRE|NOVEMBRE|DICEMBRE'
DATE=re.compile(r'(LUNED[IÌ]|MARTED[IÌ]|MERCOLED[IÌ]|GIOVED[IÌ]|VENERD[IÌ]|SABATO|DOMENICA)\s+\d{1,2}\s+(?:'+MONTH+r')',re.I)
PLACES=['SANTA MARIA IMBARO','ROCCA SAN GIOVANNI','ROCCA S. GIOVANNI','SAN VITO CHIETINO','TORINO DI SANGRO','LAMA DEI PELIGNI','FARA SAN MARTINO','CASALBORDINO','GUARDIAGRELE','COLLEDIMEZZO','FOSSACESIA','LANCIANO','ORTONA','PALENA','ATESSA','VASTO']
META=re.compile(r'^(ORE|DALLE|INFO|C/O|RITROVO|PUNTO DI RITROVO|PIAZZA|VILLA|VIA |LIDO|SPIAGGIA|AGRITURISMO|CHIESA|AUDITORIUM|STAZIONE)',re.I)
def clean(x): return re.sub(r'\s+',' ',x or '').strip(' #\n\t')
def nice(x): return x.lower().title().replace('Rocca S. Giovanni','Rocca San Giovanni')
def norm(x): return unicodedata.normalize('NFKD',x).encode('ascii','ignore').decode().upper()
def lines(doc):
 out=[]
 for pno in range(1,doc.page_count):
  page=doc[pno]; w=page.rect.width; cols=[[],[],[]]
  for b in page.get_text('dict')['blocks']:
   for ln in b.get('lines',[]):
    for sp in ln['spans']:
     t=clean(sp['text'])
     if t: cols[min(2,max(0,int(sp['bbox'][0]/w*3)))].append({'t':t,'x':sp['bbox'][0],'y':sp['bbox'][1],'s':sp['size'],'b':'bold' in sp['font'].lower()})
  for ci,col in enumerate(cols):
   rows=[]
   for sp in sorted(col,key=lambda z:(z['y'],z['x'])):
    r=next((q for q in rows if abs(q['y']-sp['y'])<2.4),None)
    if not r: r={'y':sp['y'],'v':[],'s':0,'b':False};rows.append(r)
    r['v'].append(sp);r['s']=max(r['s'],sp['s']);r['b']|=sp['b']
   for r in sorted(rows,key=lambda q:q['y']): out.append({'c':ci,'t':clean(' '.join(z['t'] for z in sorted(r['v'],key=lambda z:z['x']))),'s':r['s'],'b':r['b']})
 return out
def parse(rows):
 sizes=sorted(r['s'] for r in rows); med=sizes[len(sizes)//2] if sizes else 10; date='Tutti i giorni';place='';cur=None;out=[]
 def flush():
  nonlocal cur
  if cur:
   cur['descrizione']=clean(' '.join(cur.pop('_b')));out.append(cur)
  cur=None
 for r in rows:
  t=clean(r['t']);u=norm(t)
  if not t:continue
  if 'TUTTI I GIORNI' in u:flush();date='Tutti i giorni';continue
  m=DATE.search(u)
  if m:flush();date=nice(m.group());rest=u.replace(m.group(),' ');place=nice(next((p for p in PLACES if p in rest),place));continue
  if u.replace('.','').replace(':','').strip() in PLACES:flush();place=nice(u.replace('.','').replace(':','').strip());continue
  if re.match(r'^(DAL \d|DA NON PERDERE|ARTE & MUSICA|FIERA|PRODOTTI TIPICI)',t,re.I):continue
  title=not META.match(t) and 3<=len(t)<=110 and not t.endswith(('.', '!', '?')) and (r['b'] or r['s']>=med*1.1 or len(t.split())<=5)
  if title:flush();cur={'data':date,'titolo':t,'localita':place or 'Costa dei Trabocchi','orario':'','luogo':'','info':'','_b':[]};continue
  if not cur:continue
  im=re.search(r'Info\s*:\s*(.+)$',t,re.I)
  if im:cur['info']=clean(im.group(1));t=clean(t[:im.start()])
  tm=re.search(r'\b(?:Ore|Dalle(?: ore)?)\s+\d{1,2}(?:[.:,]\d{2})?(?:\s*(?:e|alle)\s*\d{1,2}(?:[.:,]\d{2})?)?',t,re.I)
  if tm:cur['orario']=tm.group();t=clean(t[:tm.start()]+' '+t[tm.end():])
  if META.match(t) and not cur['luogo']:cur['luogo']=t
  elif t and not re.match(r'^\*?sconto',t,re.I):cur['_b'].append(t)
 flush();return out
def main():
 doc=fitz.open(PDF);ls=lines(doc);events=[]
 for c in range(3):events+=parse([r for r in ls if r['c']==c])
 seen=set();events=[e for e in events if not(norm('|'.join([e['data'],e['titolo'],e['localita']])) in seen or seen.add(norm('|'.join([e['data'],e['titolo'],e['localita']]))))]
 if len(events)<2:raise SystemExit('Eventi riconosciuti insufficienti')
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text('window.CAREZZA_EVENTS='+json.dumps({'fonte':PDF.name,'eventi':events},ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
 OUT.with_name('estrazione-log.txt').write_text(f'OK: {len(events)} eventi estratti da {doc.page_count} pagine.\n',encoding='utf-8')
if __name__=='__main__':main()
