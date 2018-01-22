[![License](https://img.shields.io/github/license/scriptotek/humord.svg)](https://creativecommons.org/publicdomain/zero/1.0/)
[![Build Status](https://travis-ci.org/scriptotek/humord.svg?branch=test-travis)](https://travis-ci.org/scriptotek/humord)
[![GitHub repo size in bytes](https://img.shields.io/github/repo-size/scriptotek/humord.svg)]()

## HUMORD

[HUMORD](http://www.bibsys.no/files/out/humord/) is a subject thesaurus
maintained in BIBSYS' emnemodul and exported as XML to
<http://www.bibsys.no/files/out/humordsok/humord.xml> every Monday morning.

### Innhold

Contents of this repo:

* `src/humord.xml` : Source data from BIBSYS' emnemodul.
* `humord.json` : Converted to RoaldIII JSON.
* `dist/humord.ttl` : Converted to RDF Turtle, with mappings mixed in.
* `dist/humord.marc21.xml` : Converted to MARC21 XML, with DDC mappings mixed in.

### Conversion

Authority data is currently maintained in Bibsys and converted to
JSON (RoaldIII data model) using [RoaldIII](https://github.com/realfagstermer/roald).
RoaldIII is also used to mix in mappings before exporting
RDF/SKOS and MARC21.

* `pip install -r requirements.txt` to install dependencies needed for the conversion.
* `doit build` to do the actual conversion. This only runs if any of the source files
have changed or any of the target files are missing. To force a conversion even if no
files have changed, run `doit forget build && doit build` (useful during development).

Please see the RoaldIII repo for more details on the conversion.

The RoaldIII JSON data is found in `humord.json`.
Complete, distributable RDF/SKOS and MARC21 files are found in the
`dist` folder. These includes mappings.

### Konverteringsprosessen

I registerfilen er hver term angitt som et `<post>`-element. Dette har
underelementer som `<term-id>`, `<hovedemnefrase>`, osv. Under vises
vår foreløpige modell for mapping av disse elementene til RDF, som
implementert i `convert.xq`. Vi bruker hovedsakelig
[SKOS-vokabularet](http://www.w3.org/2004/02/skos/core.html).


- Hvis posten har `<se-id>`:
  ```turtle
  <http://data.ub.uio.no/humord/<se-id> a skos:Concept
      skos:altLabel "<hovedemnefrase> (<kvalifikator>)"@nb
  ```

- Ellers:
  ```turtle
  <http://data.ub.uio.no/humord/<term-id> a skos:Concept
      skos:prefLabel "<hovedemnefrase> (<kvalifikator)>"@nb
      skos:inScheme <http://data.ub.uio.no/humord/>
      dcterms:identifier "<term-id>"
      dcterms:modified "<dato>"^^xs:date
      skos:definition "<definisjon>"@nb
      skos:editorialNote "<noter>"@nb
      skos:editorialNote "Lukket bemerkning: <lukket-bemerkning>"@nb
      skos:scopeNote "Se også: <gen-se-ogsa-henvisning>"@nb
      skos:broader <http://data.ub.uio.no/humord/<overordnetterm-id>
      skos:broader <http://data.ub.uio.no/humord/<ox-id>
      skos:related <http://data.ub.uio.no/humord/<se-ogsa-id>
  ```



#### Merknader og åpne spørsmål

* **Se-henvisninger (SE)** mappes til `skos:altLabel` med selve termene som enkle
  literaler. De beholder ikke egne identifikatorer, slik de har i den nåværende
  HUMORD-modellen. Om vi skulle ønske å beholde identifikatorene, kan vi
  uttrykke termene som `skosxl:Label` fremfor literaler, men det kompliserer
  modellen og er derfor fristende å unngå med mindre vi faktisk har en god
  grunn til å gjøre det.

* **Generelle se-henvisninger (GE)** *ignoreres* foreløpig. Vi har 392 av disse
  ([liste](https://gist.github.com/danmichaelo/bb9c23fe266da8850d90)).
  Dersom vi skulle ønske å inkludere de kan vi bruke
  `isothes:SplitNonPreferredTerm` fra [ISO 25964 SKOS extension](http://lov.okfn.org/dataset/lov/details/vocabulary_iso-thes.html),
  som er en utvidelse av `skosxl:Label`. Eks:

  ```turtle
  :9767 a isothes:PreferredTerm ,
      isothes:lexicalValue "Språk" ,
      isothes:identifier "HUME09767" .

  :3680 a isothes:PreferredTerm ,
      isothes:lexicalValue "Norden" ,
      isothes:identifier "HUME03680" .

  :10249 a isothes:SplitNonPreferredTerm ,
      isothes:lexicalValue "Nordisk språk"@nb ,
      isothes:identifier "HUME10249" .

  :c1 a isothes:CompoundEquivalence ,
      isothes:plusUF <:10249>
      isothes:plusUse <:9767>, <:3680>
  ```
  Merk at dette er relasjoner mellom termer, ikke begreper, så det representerer
  et ganske markant brudd med SKOS-modellen. Men det går selvfølgelig an å tilby
  både en isothes-basert RDF og en SKOS-basert RDF.

* **Fasettindikatorer**: Vi har 175 slike (`<type>F</type>`). Disse mappes til `isothes:ThesaurusArray` og `skos:Collection`.
  Eksempel:

  ```turtle
  <humord/c00102> a isothes:ThesaurusArray,
        skos:Collection ;
    dct:identifier "HUME00102" ;
    dct:modified "1994-03-21"^^xsd:date ;
    skos:inScheme <humord> ;
    skos:member <humord/c00103>,
        <humord/c00105>,
        <humord/c00106>,
        <humord/c00107>,
        <humord/c00109>,
        <humord/c16312>,
        <humord/c18224>,
        <humord/c19001>,
        <humord/c19427>,
        <humord/c25561>,
        <humord/c25928>,
        <humord/c27930> ;
    skos:prefLabel "(arkeologi etter type)"@nb .
  ```
  (Foreløpig uløst problem: `dct:modified` reflekterer ikke når det sist ble gjort endringer i medlemslisten.)

  I MARC21-representasjonen får de `008/15 = "b"` for å markere at disse ikke skal brukes i emneinnførsler,
  og `008/09 = "e"` for å markere at de er fasettindikatorer ("node label").

* **Knutetermer** (hjelpetermer): Vi har 132 slike (`<type>K</type>`). Disse brukes ikke i indeksering, bare for å "knytte hierarkier sammen".
  De konverteres som vanlig, men får `rdf:type bs:KnuteTerm` så de enkelt kan identifiseres ved behov.
  I MARC21-representasjonen får de `008/15 = "b"` for å markere at disse ikke skal brukes i emneinnførsler.

  Eksempel:
  ```turtle
  <http://data.ub.uio.no/humord/00008> a bs:KnuteTerm, skos:Concept ;
  ```

* **Topptermer** (`<toppterm-id>`): Legger til `skos:topConceptOf <http://data.ub.uio.no/humord/>`.
 Humord har 26 stk. I XML-filen fra Bibsys har disse i tillegg en hierarkisk relasjon til HUME00001, men denne ignoreres i konverteringen. Toppbegreper med overordnede blir for dumt :)

* **Underemnefrase** (`<underemnefrase>`) er ikke brukt i HUMORD.

### Oppdatering

*(UTDATERT)*

Bibsys legger ut oppdatert Humord-XML hver mandag klokka 07 UTC.
0715 henter vi filen, konverterer til RDF, gjør en commit og dytter til utv.uio.no.
(Zorba og Jena må ligge i PATH)

    PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/opt/zorba-3.0/bin:/data/apache-jena-2.10.0/bin/
    15 7 * * 1 cd /projects/datakilder && ./tools/publish.sh humord 2>&1 | tee out.log

0730 oppdaterer vi Fuseki på en annen maskin. I crontab settes `RUBYENV` til verdien
fra `rvm env --path`:

    RUBYENV=/usr/local/rvm/environments/ruby-1.9.3-p551@global
    30 7 * * 1 cd /opt/datakilder && git pull uio master && ./tools/update-fuseki.sh humord

### Lisens

Dataene ble lagt ut i forbindelse med prosjektet
[tesaurus-mapping](http://www.ub.uio.no/om/prosjekter/tesaurus/)
høsten 2014.
De er tilgjengelige under [CC0 1.0](//creativecommons.org/publicdomain/zero/1.0/deed.no).
