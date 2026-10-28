import json,sys,glob,os,collections
d=sys.argv[1]
rows=collections.defaultdict(list)
tot=collections.Counter()
for f in sorted(glob.glob(os.path.join(d,'*.json'))):
    b=os.path.basename(f)[:-5]
    opp,rest=b.split('-',1) if not b.startswith('apex22') else ('apex22',b[7:])
    if b.startswith('apex-'): opp,rest='apex',b[5:]
    m,side=rest.rsplit('-',1)
    j=json.load(open(f))
    us='team'+side
    g={t['team']:int(t['submittedGems']) for t in j['teams']}
    them='teamB' if side=='A' else 'teamA'
    st=collections.Counter()
    for c in j['champions']:
        mm=c['metrics']; k='u' if c['team']==us else 't'
        st[k+'d']+=int(mm['deaths']); st[k+'k']+=int(mm['kills']); st[k+'mon']+=mm['monsterDamageDone']; st[k+'gold']+=int(mm['earnedGold'])
    won=j['match']['outcome']==us
    rows[m].append((opp,side,won,g[us],g[them],st['ud'],st['td'],int(st['umon']),int(st['tmon']),j['match']['roundsCompleted']))
    for k,v in st.items(): tot[k]+=v
    tot['w']+=won; tot['n']+=1
for m,rs in rows.items():
    w=sum(r[2] for r in rs)
    print(f"{m:<22} {w}/{len(rs)} "+" ".join(f"{r[0][4:] or 'x'}{r[1]}:{'W' if r[2] else 'l'}{r[3]}-{r[4]} d{r[5]}/{r[6]}" for r in rs))
print(dict(tot))
