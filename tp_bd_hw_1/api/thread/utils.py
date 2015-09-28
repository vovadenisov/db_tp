from json import dumps, loads
from django.db import DatabaseError, IntegrityError

get_thread_by_id_query = '''SELECT thread.date, thread.dislikes, forum.short_name, thread.id, 
                                   thread.isClosed, thread.isDeleted, thread.likes, thread.messages,
                                   thread.likes - thread.dislikes as points, posts.count as posts, thread.slug, thread.title, user.email
                            FROM thread INNER JOIN user
                            ON thread.user_id = user.id
                            INNER JOIN forum ON forum.id = thread.forum_id
                            INNER JOIN (SELECT thread_id, COUNT(*) as count
                                        FROM posts
                                        GROUP BY thread_id) posts ON posts.thread_id = thread.id
                            WHERE thread.id = %s;
                        '''

def get_thread_by_id(cursor, thread_id):
    thread = cursor.execute(get_thread_by_id_query, [thread_id, ]).fetch_one()
    return {"date": thread[0],
            "dislikes": thread[1],
            "forum": thread[2],
            "id": thread[3],
            "isClosed": thread[4],
            "isDeleted": thread[5],
            "likes": thread[6],
            "message": thread[7],
            "points": thread[8],
            "posts": thread[9],
            "slug": thread[10],
            "title": thread[11],
            "user": thread[12]
           }
