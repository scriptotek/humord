.PHONY: ttl solr clean
.DEFAULT_GOAL := ttl

ttl: humord.ttl
solr: humord_solr.json

humord_solr.json: humord.ttl
	python ./tools/ttl2solr.py -v humord.ttl humord_solr.json

humord.ttl: humord.tmp.ttl
	rm -f skosify.log
	python ./tools/skosify-sort.py -b 'http://data.ub.uio.no/' -o humord.ttl vocabulary.ttl humord.tmp.ttl

humord.tmp.ttl: humord.rdf.xml
	# update is part of jena/arq
	update --update=fix-thesaurusarray.ru --data=humord.rdf.xml --dump > humord.tmp.ttl

humord.rdf.xml: tools humord.xml
	cd tools && \
	git pull && \
	cd .. && \
    zorba -i tools/emneregister2rdf.xq -e "base:=hume" -e "scheme:=http://data.ub.uio.no/humord" -e "file:=../humord.xml" >| humord.rdf.xml

tools:
	git clone https://github.com/danmichaelo/ubdata-tools.git tools

humord.xml:
	curl -s -o humord.xml http://www.bibsys.no/files/out/humordsok/HUMEregister.xml

clean:
	rm -f skosify.log
	rm -f humord.rdf.xml
	rm -f humord.ttl
	rm -f humord.tmp.ttl
	rm -f humord.xml
