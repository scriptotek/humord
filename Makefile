.PHONY: HUMEregister.xml

all: HUMEregister.ttl

HUMEregister.ttl: HUMEregister.rdf.xml
	rapper -i rdfxml -o turtle HUMEregister.rdf.xml >| HUMEregister.ttl

HUMEregister.rdf.xml: HUMEregister.xml
	zorba -i convert.xq >| HUMEregister.rdf.xml

HUMEregister.xml:
	wget http://www.bibsys.no/files/out/humordsok/HUMEregister.xml

clean:
	rm HUMEregister.rdf.xml
	rm HUMEregister.ttl
	rm HUMEregister.xml
