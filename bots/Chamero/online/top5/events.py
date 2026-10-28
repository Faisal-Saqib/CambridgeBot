import json,glob,collections,sys
show={}
for f in glob.glob('show-*.json'):
    for x in json.load(open(f))['matches']: show[(x['map'],[t['name'] for t in x['teams'] if t['name']!='Quantum Wardens'][0])]=x
def load(m,t):
    x=show[(m,t)]; j=json.load(open(f"match-{x['matchId']}.json"))
    us='team'+[q for q in x['teams'] if q['name']=='Quantum Wardens'][0]['side'].upper()
    return j,us
j,us=load('00great_wall','Mite')
for e in j['events']:
    if e['entries']: print(e['kind'], e['owner']['name'], e['owner']['team'], json.dumps(e['entries'][:2])[:400]); 

print()
for m in ['00great_wall','00expanse','01boss_battle']:
  for t in ['Mite','Intercontinental Fish','newer team','Ad Astra','print dont int']:
    j,us=load(m,t)
    c=collections.defaultdict(collections.Counter)
    for e in j['events']:
        k='us' if e['owner']['team']==us else 'th'
        for en in e['entries']:
            c[k][e['kind']]+=1
            if e['kind']=='gemSubmission': c[k]['subgems']+=int(en['value'])
            if e['kind']=='gemCollection': c[k]['colgems']+=int(en['value'])
            if e['kind']=='death' and en['context']=='camp': c[k]['campdeath']+=1
    f=lambda k: f"clears {c[k]['campClear']:>3} caps {c[k]['gemCollection']:>3} tributes {c[k]['gemSubmission']:>3} avg {c[k]['subgems']//max(1,c[k]['gemSubmission']):>3} deaths {c[k]['death']}(camp {c[k]['campdeath']}) fuelX {c[k]['fuelExhausted']}"
    print(f"{m:<13}{t[:12]:<13} US {f('us')} | THEM {f('th')}")

print("\nwhere each team's clears are (our half / their half), by game phase")
for m in ['00great_wall','00expanse']:
  for t in ['Mite','Intercontinental Fish','newer team','Ad Astra','print dont int']:
    j,us=load(m,t)
    spawn={}
    for e in j['events']:
        if e['kind']=='buyItem' and e['entries']:
            spawn.setdefault(e['owner']['team'],(e['entries'][0]['x'],e['entries'][0]['y']))
    th=[k for k in spawn if k!=us][0]
    su,st=spawn[us],spawn[th]
    d=lambda a,b: max(abs(a[0]-b[0]),abs(a[1]-b[1]))
    c=collections.Counter()
    for e in j['events']:
        if e['kind']!='campClear': continue
        k='us' if e['owner']['team']==us else 'th'
        for en in e['entries']:
            p=(en['x'],en['y']); half='ourside' if d(p,su)<d(p,st) else 'theirside'
            ph='early' if en['timestamp']['round']<300 else 'mid'
            c[(k,half,ph)]+=1
    print(f"{m:<13}{t[:12]:<13} US: early {c['us','ourside','early']}/{c['us','theirside','early']} mid {c['us','ourside','mid']}/{c['us','theirside','mid']}  | THEM: early {c['th','ourside','early']}/{c['th','theirside','early']} mid {c['th','ourside','mid']}/{c['th','theirside','mid']}")
