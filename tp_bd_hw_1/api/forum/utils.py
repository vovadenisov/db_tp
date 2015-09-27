from json import dumps, loads
from django.db import DatabaseError, IntegrityError

get_forum_by_id_query = '''SELECT forum.id, forum.name, forum.short_name, user.email
                           FROM forum INNER JOIN user
                           ON forum.user_id = user.id
                           WHERE forum.id = %s;
                        '''

get_forum_by_id(cursor, forum_id)
    forum = cursor.execute(get_forum_by_id_query, [forum_id]).fetch_one()
    return {"id": forum[0],
            "name": forum[1],
            "short_name": forum[2],
            "user": forum[3]
           }
