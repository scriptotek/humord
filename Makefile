.PHONY: humord.xml

all: humord.ttl

humord.ttl: humord.tmp.ttl
	rm -f skosify.log
	../tools/skosify-sort/skosify-sort.py -c skosify.ini vocabulary.ttl humord.tmp.ttl -o humord.ttl

humord.tmp.ttl: humord.rdf.xml
	rapper -i rdfxml -o turtle humord.rdf.xml >| humord.tmp.ttl

humord.rdf.xml: humord.xml
	zorba -i convert.xq >| humord.rdf.xml

humord.xml:
	wget -nv -O humord.xml http://www.bibsys.no/files/out/humordsok/HUMEregister.xml

clean:
	rm -f skosify.log
	rm -f humord.rdf.xml
	rm -f humord.ttl
	rm -f humord.tmp.ttl
	rm -f humord.xml
