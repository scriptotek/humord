
<posts>
{
	for $post in doc("humord.xml")/hume/post[gen-se-henvisning]
	return $post
}
</posts>