.PHONY: humord.xml

all: humord.ttl

humord.ttl: humord.tmp.ttl
	rm -f skosify.log
	../tools/skosify-sort/skosify-sort.py -b 'http://data.ub.uio.no/' -o humord.ttl vocabulary.ttl humord.tmp.ttl
	rm -f humord.tmp.ttl

humord.tmp.ttl: humord.rdf.xml
	# update is part of jena/arq
	update --update=fix-thesaurusarray.ru --data=humord.rdf.xml --dump > humord.tmp.ttl

humord.rdf.xml: humord.xml
	zorba -i convert.xq >| humord.rdf.xml

humord.xml:
	curl -s -o humord.xml http://www.bibsys.no/files/out/humordsok/HUMEregister.xml

clean:
	rm -f skosify.log
	rm -f humord.rdf.xml
	rm -f humord.ttl
	rm -f humord.tmp.ttl
	rm -f humord.xml
