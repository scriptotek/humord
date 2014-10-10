(: Return all distinct element names :)

<nodes>
{
	for $x in distinct-values(doc('HUMEregister.xml')//*/name())
	return element {$x} {''}
}
</nodes>
