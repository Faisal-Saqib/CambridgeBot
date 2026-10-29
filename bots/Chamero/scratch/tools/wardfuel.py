import json,glob,sys
for d in sys.argv[1:]:
    w=f=n=0
    for p in glob.glob(d+'/*.json'):
        side=p[-6]; us='team'+side; j=json.load(open(p)); n+=1
        for e in j['events']:
            if e['owner']['team']!=us: continue
            if e['kind']=='wardPlacement': w+=len(e['entries'])
            if e['kind']=='fuelExhausted': f+=len(e['entries'])
    print(d, 'wards/game', round(w/n,1), 'fuelX/game', round(f/n,1))
