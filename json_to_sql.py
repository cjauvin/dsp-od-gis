import sys
import json
from collections import namedtuple
from pprint import pprint
from psycopg2.extensions import register_adapter, AsIs
from little_pger import LittlePGer

dbname = sys.argv[1]
srid = int(sys.argv[2])

Unquoted = namedtuple('Unquoted', ['s'])
register_adapter(Unquoted, lambda u: AsIs(u.s))

pg = LittlePGer(f'dbname={dbname}', commit=True)

def get_point_geom(a, k):
    return Unquoted(f"st_pointfromtext('point(%s)', {srid})" % ' '.join(map(str, a[k])))

i = 0
for line in sys.stdin:

    i += 1
    if i == 1: continue

    try:
        o = json.loads(line.strip(',\n'))
    except json.decoder.JSONDecodeError as e:
        break

    for f in o:
        o[f.lower()] = o.pop(f)

    for f in ['origin', 'destination']:
        if f in o:
            o[f] = get_point_geom(o, f)

    steps = o.pop('steps', [])

    od = pg.insert('od', values=o)

    for s in steps:

        s['od_id'] = od['od_id']

        for f in s:
            s[f.lower()] = s.pop(f)

        if 'stopcoordinates' in s:
            s['stopcoordinates'] = get_point_geom(s, 'stopcoordinates')

        if 'geojson' in s:
            geom = s['geojson']['geometry']
            # https://gis.stackexchange.com/a/60945/5024
            geom['crs'] = {"type": "name", "properties": {"name": f"EPSG:{srid}"}}
            s['geom'] = Unquoted("st_geomfromgeojson('%s')" % json.dumps(geom))
            s['geojson'] = json.dumps(s['geojson'])

        pg.insert('od_step', values=s)

    if i % 10000 == 0:
        print(i)

pg.commit()
