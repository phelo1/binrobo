Q='[out:json][timeout:50];(way(around:700,53.000000,-8.000000)["highway"];);out geom tags;'
for i in 1 2 3; do for u in https://overpass-api.de/api/interpreter https://lz4.overpass-api.de/api/interpreter https://z.overpass-api.de/api/interpreter https://overpass.kumi.systems/api/interpreter; do
curl -s -m 55 --data-urlencode "data=$Q" $u -o tmp_osm.json && python3 -c "import json;json.load(open('tmp_osm.json'))" 2>/dev/null && mv tmp_osm.json osm_ways.json && echo OK $u && exit 0; echo fail $u; done; done
