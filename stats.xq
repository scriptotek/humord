import module namespace emneregister="http://ub.uio.no/emneregister"
  at "../emneregister.xq";

emneregister:stats( doc( 'humord.xml' )/hume/post )
