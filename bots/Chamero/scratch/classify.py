import re,glob,os,json,sys
S=sys.argv[1]; picks=json.load(open(sys.argv[2]))
rows=[]
for f in sorted(glob.glob(S+'/*.txt')):
    m=os.path.basename(f)[:-4]; t=open(f,errors='ignore').read()
    h=re.search(r'SCAN map (\d+)x(\d+) altars (\d+) groups (\d+) total_gems (\d+) brawl (\w+)',t)
    w,hh,alt,ng,tg,br=h.groups(); w,hh=int(w),int(hh)
    gs=[dict(zip(['gems','gold','hp','dps','n','dus','dthem'],map(float,x[:7])),mono=x[7]=='true') for x in re.findall(r'SCANG \d+ gems (\d+) gold (\d+) hp (\d+) dps (\d+) n (\d+) dus (\d+) dthem (\d+) mono (\w+)',t)]
    gems=sum(g['gems'] for g in gs); gold=sum(g['gold'] for g in gs)
    harmless=sum(g['gems'] for g in gs if g['dps']==0)/max(gems,1)
    mono=sum(g['gems'] for g in gs if g['mono'])/max(gems,1)
    top=max(g['gems'] for g in gs)/max(gems,1)
    mine=sum(g['gems'] for g in gs if g['dus']<g['dthem'])
    mid=sum(g['gems'] for g in gs if g['dus']==g['dthem'])/max(gems,1)
    hp=sum(g['hp'] for g in gs)
    p=picks.get(m,5)
    dens=gems/(w*hh)*1000
    rows.append(dict(map=m,size=f"{w}x{hh}",picks=p,altars=int(alt),groups=len(gs),gems=int(gems),gold=int(gold),gems_per_champ=round(gems/p),gold_per_champ=round(gold/p),density=round(dens,1),harmless=round(harmless,2),mono=round(mono,2),top=round(top,2),center=round(mid,2),hp_per_gem=round(hp/max(gems,1)),brawl=br=='true'))
for r in rows:
    gpc=r['gems_per_champ']
    r['class']= 'jackpot' if r['top']>=0.5 else ('boss' if r['mono']>=0.5 else ('rich' if gpc>=90 else ('sparse' if gpc<50 else 'normal')))
json.dump(rows,open(S+'/../maps.json','w'),indent=1)
print(f"{'map':<22}{'size':>7}{'pk':>3}{'alt':>4}{'grp':>4}{'gems':>5}{'gold':>6}{'g/ch':>5}{'au/ch':>6}{'harm':>5}{'mono':>5}{'top':>5}{'ctr':>5}{'hp/g':>5}  class")
for r in sorted(rows,key=lambda r:(r['class'],-r['gems_per_champ'])):
    print(f"{r['map']:<22}{r['size']:>7}{r['picks']:>3}{r['altars']:>4}{r['groups']:>4}{r['gems']:>5}{r['gold']:>6}{r['gems_per_champ']:>5}{r['gold_per_champ']:>6}{r['harmless']:>5}{r['mono']:>5}{r['top']:>5}{r['center']:>5}{r['hp_per_gem']:>5}  {r['class']}")
import collections; print(collections.Counter(r['class'] for r in rows))
