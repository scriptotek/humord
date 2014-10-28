## HUMORD

### Innhold

[HUMORD](http://www.bibsys.no/files/out/humord/) er en emnetesaurus som
vedlikeholdes i BIBSYS' emnemodul, og eksporteres som XML hver mandag
til <http://www.bibsys.no/files/out/humordsok/HUMEregister.xml>

* `HUMEregister.xml` : Registeret som eksportert fra BIBSYS' emnemodul.
* `HUMEregister.ttl` : Registeret konvertert til RDF og serialisert som Turtle.
* `convert.xq` : XQuery-script for å konvertere `HUMEregister.xml` til RDF.

### Konverteringsprosessen

I registerfilen er hver term angitt som et `<post>`-element. Dette har
underelementer som `<term-id>`, `<hovedemnefrase>`, osv. Under vises
vår foreløpige modell for mapping av disse elementene til RDF, som
implementert i `convert.xq`. Vi bruker hovedsakelig
[SKOS-vokabularet](http://www.w3.org/2004/02/skos/core.html).

    if <se-id> then

      <http://data.ub.uio.no/humord/<se-id> a skos:Concept
        skos:altLabel "<hovedemnefrase> (<kvalifikator>)"@nb

    else:

      <http://data.ub.uio.no/humord/<term-id> a skos:Concept
        skos:prefLabel "<hovedemnefrase> (<kvalifikator)>"@nb
        dcterms:identifier "<term-id>"
        dcterms:modified "<dato>"^^xs:date
        skos:definition "<definisjon>"@nb
        skos:editorialNote "<noter>"@nb
        skos:editorialNote "Lukket bemerkning: <lukket-bemerkning>"@nb
        skos:scopeNote "Se også: <gen-se-ogsa-henvisning>"@nb
        skos:broader <http://data.ub.uio.no/humord/<overordnetterm-id>
        skos:broader <http://data.ub.uio.no/humord/<ox-id>
        skos:related <http://data.ub.uio.no/humord/<se-ogsa-id>

#### Merknader

* Se-henvisninger mappes til skos:altLabel. De beholder ikke egne identifikatorer.
  Vi *kan* beholde disse ved å bruke SKOS-XL, men foreløpig seg jeg ikke noe poeng
  med det.
  Må diskuteres!

* Generelle se-henvisninger *ignoreres*. Vi har 392 av disse
  ([liste](https://gist.github.com/danmichaelo/bb9c23fe266da8850d90)).
  Det er usikkert om det gir mening å bruke disse i mappingøyemed.
  Må diskuteres.

* '`<type>' ignoreres foreløpig, og postene behandles som andre poster.
  Vi har 132 knutetermer (type=K) og 175 fasettindikatorer (type=F).
  Må diskuteres om vi skal behandle disse spesielt.

* Elementet `<toppterm-id>` ignoreres.

* Elementet `<underemnefrase>` er ikke brukt i HUMORD.

### Bruk:

XQuery-scriptet kan kjøres med f.eks. [Zorba](http://www.zorba.io/):

    $ zorba -i convert.xq >| HUMEregister.rdf.xml

Konvertering fra RDF/XML til RDF/Turtle kan gjøres med f.eks.
[Rapper](http://librdf.org/raptor/rapper.html):

    $ rapper -i rdfxml -o turtle HUMEregister.rdf.xml >| HUMEregister.ttl

Har du Zorba og installert kan du kjøre `make clean && make` for å hente
en ny XML fra Bibsys, og utføre begge kommandoene ovenfor.

### Oppdatering

Hver mandag klokka 12:
```
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/opt/zorba-3.0/bin

0 12 * * 1 cd /projects/datakilder/humord && ./publish.sh 2>&1 | tee out.log
```

### Lisens

Dataene ble lagt ut i forbindelse med prosjektet
[tesaurus-mapping](http://www.ub.uio.no/om/prosjekter/tesaurus/)
høsten 2014.
De er tilgjengelige under [CC0 1.0](//creativecommons.org/publicdomain/zero/1.0/deed.no).
