.PHONY: HUMEregister.xml

all: HUMEregister.ttl

HUMEregister.ttl: HUMEregister.tmp.ttl
	rm skosify.log
	../tools/skosify-sort/skosify-sort.py -c skosify.ini vocabulary.ttl HUMEregister.tmp.ttl -o HUMEregister.ttl

HUMEregister.tmp.ttl: HUMEregister.rdf.xml
	rapper -i rdfxml -o turtle HUMEregister.rdf.xml >| HUMEregister.tmp.ttl

HUMEregister.rdf.xml: HUMEregister.xml
	zorba -i convert.xq >| HUMEregister.rdf.xml

HUMEregister.xml:
	wget -nv http://www.bibsys.no/files/out/humordsok/HUMEregister.xml

clean:
	rm skosify.log
	rm HUMEregister.rdf.xml
	rm HUMEregister.ttl
	rm HUMEregister.tmp.ttl
	rm HUMEregister.xml
