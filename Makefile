.DEFAULT_GOAL := rdf
.PHONY: rdf solr toolsupdate clean

gitmaster := ./tools/.git/refs/heads/master
basename = data/humord

# If make does create b in order to update something else, it deletes
# b later on after it is no longer needed.
.INTERMEDIATE: $(basename).rdf.xml $(basename).tmp.ttl

rdf: toolsupdate $(basename).ttl
solr: toolsupdate solr/humord.json

tools:
	git clone https://github.com/danmichaelo/ubdata-tools.git tools

toolsupdate: tools
	cd ./tools && git pull && cd ..
	# touch ./tools/.git/refs/heads/master

$(basename).ttl: $(basename).tmp.ttl $(gitmaster)
	rm -f skosify.log
	python ./tools/skosify-sort.py -b 'http://data.ub.uio.no/' -o $@ vocabulary.ttl $(basename).tmp.ttl

# update is part of jena/arq
$(basename).tmp.ttl: $(basename).rdf.xml
	update --update=fix-thesaurusarray.ru --data=$(basename).rdf.xml --dump > $@

$(basename).rdf.xml: $(basename).xml $(gitmaster)
	zorba -i ./tools/emneregister2rdf.xq -e "base:=hume" -e "scheme:=http://data.ub.uio.no/humord" \
	  -e "file:=../$(basename).xml" >| $@

$(basename).xml:
	curl -s -o $@ http://www.bibsys.no/files/out/humordsok/HUMEregister.xml

solr/humord.json: $(basename).ttl $(gitmaster)
	python ./tools/ttl2solr.py -v $(basename).ttl $@

clean:
	rm -f skosify.log
	rm -f $(basename).rdf.xml
	rm -f $(basename).ttl
	rm -f $(basename).tmp.ttl
	rm -f $(basename).xml
