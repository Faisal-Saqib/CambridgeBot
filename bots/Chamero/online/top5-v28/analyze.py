import json,glob,collections
def at(runs,r):
    t=0;v=0
    for x in runs:
        if t>r: break
        v=float(x['value']); t+=x['duration']
    return v
groups=[g for g in json.load(open("groups.json")) if not g.get("skipped")]
rows=[]
for g in groups:
    gid=json.loads(g['stdout'])['groupId']; show=json.load(open(f'show-{gid}.json'))
    for x in show['matches']:
        j=json.load(open(f"match-{x['matchId']}.json"))
        u=[t for t in x['teams'] if t['name']=='Quantum Wardens'][0]; side='team'+u['side'].upper(); o='teamB' if side=='teamA' else 'teamA'
        gm={t['team']:int(t['submittedGems']) for t in j['teams']}
        me=[c for c in j['champions'] if c['team']==side]; th=[c for c in j['champions'] if c['team']!=side]
        S=lambda cs,k: sum(float(c['metrics'][k]) for c in cs)
        cur=collections.Counter()
        for tl in j['championTimelines']:
            k='u' if tl['owner']['team']==side else 't'
            for r in (100,300,600):
                if tl['metric'] in ('monsterDamageDone','earnedGold','deaths','submittedGems'): cur[(k,tl['metric'],r)]+=at(tl['runs'],r)
        lost=S(me,'collectedGems')-S(me,'submittedGems')
        rows.append(dict(team=g['team'],rank=g['rank'],map=x['map'],side=u['side'],res=u['result'],us=gm[side],them=gm[o],
            d=int(S(me,'deaths')),k=int(S(me,'kills')),td=int(S(th,'deaths')),camp=int(S(me,'monsterDamageDone')),tcamp=int(S(th,'monsterDamageDone')),
            gold=int(S(me,'earnedGold')),tgold=int(S(th,'earnedGold')),lost=int(lost),rounds=j['match']['roundsCompleted'],
            faults=sum(j['diagnostics']['botFaults'].values()),our=[c['name'] for c in me],their=[c['name'] for c in th],
            cur={f"{a}{b[:4]}{c}":int(v) for (a,b,c),v in cur.items()},
            champs={c['name']:(int(c['metrics']['monsterDamageDone']),int(c['metrics']['deaths']),int(c['metrics']['kills']),int(c['metrics']['earnedGold'])) for c in me},
            tchamps={c['name']:(int(c['metrics']['monsterDamageDone']),int(c['metrics']['deaths']),int(c['metrics']['kills']),int(c['metrics']['earnedGold']),[ (i['item'].replace(' Emblem of ','E-').replace(' Shard of ','s-'),i['quantity']) for i in c['items']]) for c in th}))
json.dump(rows,open('analysis.json','w'),indent=1)
print(f"{'team':<22}{'map':<14}{'s':<2}{'res':<5}{'score':>10}{'d/k':>7}{'camp us/them':>15}{'gold us/them':>14}{'lost':>5}{'rnd':>5}")
for r in rows:
    print(f"{r['team'][:21]:<22}{r['map']:<14}{r['side']:<2}{r['res']:<5}{r['us']:>5}-{r['them']:<5}{r['d']:>3}/{r['k']:<3}{r['camp']//1000:>7}k/{r['tcamp']//1000}k{r['gold']:>8}/{r['tgold']:<6}{r['lost']:>5}{r['rounds']:>5}")
w=sum(r['res']=='win' for r in rows); print('wins',w,'/',len(rows),'faults',sum(r['faults'] for r in rows))
by=collections.defaultdict(list)
for r in rows: by[r['map']].append(r)
print('\nper map (avg): score, deaths/kills, camp dmg us/them, gold us/them; and at r100/r300/r600 camp dmg us/them')
for m,rs in by.items():
    n=len(rs); a=lambda k: sum(r[k] for r in rs)//n
    c=lambda key: sum(r['cur'].get(key,0) for r in rs)//n
    print(f"  {m:<14} W{sum(r['res']=='win' for r in rs)} {a('us')}-{a('them')} d{a('d')}/k{a('k')} camp {a('camp')//1000}k/{a('tcamp')//1000}k gold {a('gold')}/{a('tgold')} | camp r100 {c('umons100')//1000}k/{c('tmons100')//1000}k r300 {c('umons300')//1000}k/{c('tmons300')//1000}k r600 {c('umons600')//1000}k/{c('tmons600')//1000}k | deaths r100 {c('udeat100')} r300 {c('udeat300')}")
print('\nopponent drafts:')
for r in rows: print(f"  {r['team'][:18]:<19}{r['map']:<14}{', '.join(r['their'])}")
