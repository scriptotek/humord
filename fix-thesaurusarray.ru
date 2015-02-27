# This SPARQL update query will
#
# - add skos:broader relations that circumvent thesaurus arrays (up to 2 levels)
# - replace ?c2 skos:broader ?c1 with ?c1 skos:member ?c2 where ?c1 a isothes:ThesaurusArray
# - remove ?c1 a skos:Concept where ?c1 a isothes:ThesaurusArray
# - remove ?c1 skos:broader ?c2 where ?c1 a isothes:ThesaurusArray
#
# This is more efficiently done with SPARQL than with XQuery
#
# Usage with arq: update --update=fix-thesaurusarray.ru --data=humord.rdf.xml --dump > out.ttl
#
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX humord: <http://data.ub.uio.no/humord/>
PREFIX isothes: <http://purl.org/iso25964/skos-thes#>

INSERT
{ ?c1 skos:member ?c2 }
WHERE
{
  ?c2 skos:broader ?c1  .
  ?c1 a isothes:ThesaurusArray .
} ;

INSERT
{ ?c3 skos:broader ?c0 }
WHERE
{
  ?c3 a skos:Concept ;
      skos:broader ?c2  .
  ?c2 a isothes:ThesaurusArray ;
      skos:broader ?c1  .
  ?c1 a isothes:ThesaurusArray ;
      skos:broader ?c0  .
  ?c0 a skos:Concept .
} ;

INSERT
{ ?c2 skos:broader ?c0 }
WHERE
{
  ?c2 a skos:Concept ;
      skos:broader ?c1  .
  ?c1 a isothes:ThesaurusArray ;
      skos:broader ?c0  .
  ?c0 a skos:Concept .
} ;

INSERT
{ ?c1 skos:broader ?c2 }
WHERE
{
  ?c2 skos:broader ?c1  .
  ?c1 a isothes:ThesaurusArray .
  ?c1 skos:broader ?c0  .
  ?c0 a skos:Concept .
} ;

DELETE
{ ?c2 skos:broader ?c1 }
WHERE
{
  ?c2 skos:broader ?c1  .
  ?c1 a isothes:ThesaurusArray .
} ;

DELETE
{ ?c1 rdf:type skos:Concept }
WHERE
{ ?c1 a isothes:ThesaurusArray } ;

DELETE
{ ?c1 skos:broader ?c2 }
WHERE
{ ?c1 a isothes:ThesaurusArray ; skos:broader ?c2 }
