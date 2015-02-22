import module namespace emneregister="http://ub.uio.no/emneregister"
  at "../emneregister.xq";

declare variable $scheme := 'http://data.ub.uio.no/humord/';
declare variable $uri_base := 'http://data.ub.uio.no/humord/c';


(: To test a specific post: :)
(: emneregister:post(doc('humord.xml')/hume/post[descendant::term-id/text()="HUME18920"]) :)

emneregister:toRdf( doc( 'humord.xml' )/hume/post, $scheme, $uri_base)
