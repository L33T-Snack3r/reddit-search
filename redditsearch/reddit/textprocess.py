indentation = '   '

post_tmpl = \
"""
<POST_ID>
{post_id}
<POST_SUBREDDIT>
{post_subreddit}
<POST_TITLE>
{post_title}
<POST_AUTHOR>
{post_author}
<UPVOTES vs DOWNVOTES>
{post_upvotes} - {post_downvotes}
<POST_CONTENT>
{post_content}
"""

comment_tmpl = \
"""
<COMMENT>
{comment_content}\n
"""

reply_tmpl = \
"""
<REPLY>
{reply_content}\n

"""

def indent_text(text: str, 
                indentation: str, 
                level: int):
    return '\n'.join(f"{indentation*level}{line}" for line in text.splitlines())