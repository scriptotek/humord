(: Return all distinct element names :)

<nodes>
{
	for $x in distinct-values(doc('humord.xml')//*/name())
	return element {$x} {''}
}
</nodes>
