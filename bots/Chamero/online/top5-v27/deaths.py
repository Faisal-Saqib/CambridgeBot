import json,glob,collections
show={}
for f in glob.glob('show-*.json'):
    for x in json.load(open(f))['matches']: show[(x['map'],[t['name'] for t in x['teams'] if t['name']!='Quantum Wardens'][0])]=x
for m in ['00the_line','00crater']:
  for t in ['Mite','Intercontinental Fish','newer team','Ad Astra','print dont int']:
    x=show[(m,t)]; j=json.load(open(f"match-{x['matchId']}.json"))
    us='team'+[q for q in x['teams'] if q['name']=='Quantum Wardens'][0]['side'].upper()
    spawn={}
    for e in j['events']:
        if e['kind']=='buyItem' and e['entries']: spawn.setdefault(e['owner']['team'],(e['entries'][0]['x'],e['entries'][0]['y']))
    d=lambda a,b: max(abs(a[0]-b[0]),abs(a[1]-b[1]))
    deaths=[]
    for e in j['events']:
        if e['kind']=='death' and e['owner']['team']==us:
            for en in e['entries']: deaths.append((en['timestamp']['round'],e['owner']['name'],en['target'].get('name',en['context']),(en['x'],en['y'])))
    # assists per our death: count enemy assist events at same round
    ass=collections.Counter()
    for e in j['events']:
        if e['kind'] in('assist','kill') and e['owner']['team']!=us:
            for en in e['entries']: ass[en['timestamp']['round']]+=1
    deaths.sort()
    them=[k for k in spawn if k!=us]
    st=spawn[them[0]] if them else (0,0); su=spawn.get(us,(0,0))
    print(f"{m} vs {t}: {len(deaths)} deaths. spawn us {su} them {st}")
    print('   ', ' '.join(f"r{r}:{v[:4]}<{k[:4]}(n{ass[r]},dUs{d(p,su)},dThem{d(p,st)})" for r,v,k,p in deaths[:14]))
