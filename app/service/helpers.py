async def define_author_name(username, show_author):
    if show_author:
        author_name = f'@{username}'
    else:
        author_name = '<i>Анонимно</i>'
        
    return author_name