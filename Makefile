.PHONY: rdf solr clean toolsupdate
.DEFAULT_GOAL := rdf

rdf: data/humord.ttl
solr: solr/humord.json

tools:
	git clone https://github.com/danmichaelo/ubdata-tools.git tools

toolsupdate:
	cd tools && git pull && cd ..

data/humord.ttl: data/humord.tmp.ttl toolsupdate
	rm -f skosify.log
	python ./tools/skosify-sort.py -b 'http://data.ub.uio.no/' -o ./data/humord.ttl vocabulary.ttl ./data/humord.tmp.ttl

data/humord.tmp.ttl: data/humord.rdf.xml
	# update is part of jena/arq
	update --update=fix-thesaurusarray.ru --data=./data/humord.rdf.xml --dump > ./data/humord.tmp.ttl

data/humord.rdf.xml: data/humord.xml toolsupdate
	zorba -i ./tools/emneregister2rdf.xq -e "base:=hume" -e "scheme:=http://data.ub.uio.no/humord" -e "file:=../data/humord.xml" >| ./data/humord.rdf.xml

data/humord.xml:
	curl -s -o ./data/humord.xml http://www.bibsys.no/files/out/humordsok/HUMEregister.xml

solr/humord.json: rdf toolsupdate
	python ./tools/ttl2solr.py -v ./data/humord.ttl ./solr/humord.json

clean:
	rm -f ./skosify.log
	rm -f ./data/humord.rdf.xml
	rm -f ./data/humord.ttl
	rm -f ./data/humord.tmp.ttl
	rm -f ./data/humord.xml
