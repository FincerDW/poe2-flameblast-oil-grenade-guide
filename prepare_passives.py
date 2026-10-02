"""Validate and embed the author's stage trees and pinned open-source atlases."""
from pathlib import Path
import base64,json,re
ROOT=Path(__file__).parent
EXPECTED_NORMAL=[18,48,66,89,120,137,149,143,146]
EXPECTED_SETS=[0,0,0,18,24,24,24,24,24]

def compile_passives(t2s):
    tree=json.loads((ROOT/'research/passive-tree.json').read_text(encoding='utf-8'))
    stages=json.loads((ROOT/'research/passive-stages.json').read_text(encoding='utf-8'))['stages']
    translations=json.loads((ROOT/'research/passive-translations.json').read_text(encoding='utf-8'))
    nodes=tree['nodes']
    assert len(stages)==9
    allocated=set()
    for index,stage in enumerate(stages):
        sets={k:set(stage[k]) for k in ('common','set1','set2')}
        assert all(len(sets[k])==len(stage[k]) for k in sets),'Duplicate exported IDs'
        assert not (sets['common']&(sets['set1']|sets['set2'])),'Common nodes must dominate weapon tags'
        ids=set.union(*sets.values());allocated|=ids
        assert all(str(i) in nodes for i in ids),'Missing author node'
        normal=sum(not nodes[str(i)].get('ascendancyId') and not nodes[str(i)].get('classStartIndex') for i in ids)
        assert normal==EXPECTED_NORMAL[index],(index,normal)
        assert len(sets['set1'])==len(sets['set2'])==EXPECTED_SETS[index]
        # Each usable weapon tree must connect to the mercenary starting node.
        for key in ('set1','set2'):
            main={i for i in sets['common']|sets[key] if not nodes[str(i)].get('ascendancyId')}|{50986}
            reached={50986};queue=[50986]
            while queue:
                for link in nodes[str(queue.pop())]['links']:
                    if link in main and link not in reached:
                        reached.add(link);queue.append(link)
            assert reached==main,f'Disconnected stage {index+1} {key} tree'
    for i in allocated:
        node=nodes[str(i)]
        assert node['name'] in translations['terms'],f'Missing Chinese name {node["name"]}'
        assert all(s in translations['stats'] for s in node['stats']),f'Missing Chinese effect {node["name"]}'
    tree['stages']=stages
    tree['terms']={en:{'tw':row['tw'],'cn':t2s.convert(row['tw']),**({'url':row['url']} if row.get('url') else {})} for en,row in translations['terms'].items()}
    tree['stats']={en:{'tw':tw,'cn':t2s.convert(tw)} for en,tw in translations['stats'].items()}
    tree['images']={};tree['atlases']={}
    for key,stem in [('skills','skills'),('frame','frame'),('background','background-mercenary')]:
        tree['images'][key]='data:image/webp;base64,'+base64.b64encode((ROOT/f'assets/passive/{stem}.webp').read_bytes()).decode()
        tree['atlases'][key]={name:row['frame'] for name,row in json.loads((ROOT/f'assets/passive/{stem}.json').read_text())['frames'].items()}
    for i in allocated:
        node=nodes[str(i)];prefix='keystoneActive' if node.get('isKeystone') else 'notableActive' if node.get('isNotable') else 'normalActive'
        assert prefix+':'+node['icon'] in tree['atlases']['skills'],f'Missing original artwork {node["name"]}'
    return tree
