import json,glob,sys,collections,os
cls={r['map']:r['class'] for r in json.load(open(sys.argv[1]))}
for d in sys.argv[2:]:
    t=collections.defaultdict(collections.Counter)
    for f in glob.glob(d+'/*.json'):
        b=os.path.basename(f)[:-5]; opp='apex22' if b.startswith('apex22-') else 'apex'
        m,side=b[len(opp)+1:].rsplit('-',1); c=cls.get(m,'?'); us='team'+side
        j=json.load(open(f)); g={x['team']:int(x['submittedGems']) for x in j['teams']}
        for k in (c,'ALL'):
            t[k]['n']+=1; t[k]['w']+=j['match']['outcome']==us; t[k]['gems']+=g[us]
            t[k]['mon']+=sum(x['metrics']['monsterDamageDone'] for x in j['champions'] if x['team']==us)
            t[k]['dead']+=sum(int(x['metrics']['deaths']) for x in j['champions'] if x['team']==us)
            t[k]['r']+=int(j['match']['roundsCompleted'])
    print(os.path.basename(d))
    for k,v in sorted(t.items()): print(f"   {k:<8} {v['w']:>3}/{v['n']:<3} gems {v['gems']//v['n']:>4} camp {int(v['mon']/v['n']):>6} deaths {v['dead']/v['n']:.1f} rounds {v['r']//v['n']}")
