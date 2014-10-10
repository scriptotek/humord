
<posts>
{
	for $post in doc("HUMEregister.xml")/hume/post[gen-se-henvisning]
	return $post
}
</posts>