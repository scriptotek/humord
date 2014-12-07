.PHONY: HUMEregister.xml

all: HUMEregister.ttl

HUMEregister.ttl: HUMEregister.tmp.ttl
	rm -f skosify.log
	../tools/skosify-sort/skosify-sort.py -c skosify.ini vocabulary.ttl HUMEregister.tmp.ttl -o HUMEregister.ttl

HUMEregister.tmp.ttl: HUMEregister.rdf.xml
	rapper -i rdfxml -o turtle HUMEregister.rdf.xml >| HUMEregister.tmp.ttl

HUMEregister.rdf.xml: HUMEregister.xml
	zorba -i convert.xq >| HUMEregister.rdf.xml

HUMEregister.xml:
	wget -nv http://www.bibsys.no/files/out/humordsok/HUMEregister.xml

clean:
	rm -f skosify.log
	rm -f HUMEregister.rdf.xml
	rm -f HUMEregister.ttl
	rm -f HUMEregister.tmp.ttl
	rm -f HUMEregister.xml
