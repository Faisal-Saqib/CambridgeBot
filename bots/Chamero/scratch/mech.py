import json,glob,sys,collections
for d in sys.argv[1:]:
    t=collections.Counter(); items=collections.Counter(); n=0
    for f in glob.glob(d+'/*.json'):
        side=f[-6]; us='team'+side
        try: j=json.load(open(f))
        except Exception: continue
        n+=1
        for c in j['champions']:
            k='u' if c['team']==us else 't'; m=c['metrics']
            t[k+'mon']+=m['monsterDamageDone']; t[k+'dead']+=int(m['deaths']); t[k+'gold']+=int(m['earnedGold']); t[k+'taken']+=m['monsterDamageTaken']; t[k+'pvp']+=m['championDamageTaken']
            if k=='u':
                for i in c['items']: items[i['item'].split(' of ')[0].replace(' Emblem','E').replace(' Shard','s')]+=int(i['quantity'])
    print(d.split('/')[-1], n, {k:int(v/n) for k,v in t.items()})
    print('  items/game', {k:round(v/n,1) for k,v in items.most_common(12)})
