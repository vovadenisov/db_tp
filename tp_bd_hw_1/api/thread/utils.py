from json import dumps, loads
from django.db import DatabaseError, IntegrityError

get_thread_by_id_query = '''SELECT thread.date, thread.dislikes, forum.short_name, thread.id, 
                                   thread.isClosed, thread.isDeleted, thread.likes, thread.message,
                                   thread.likes - thread.dislikes as points, IFNULL(posts.count, 0) as posts, 
                                   thread.slug, thread.title, user.email,
                                   forum.id, user.id
                                   
                            FROM thread INNER JOIN user
                            ON thread.user_id = user.id
                            INNER JOIN forum ON forum.id = thread.forum_id
                            LEFT JOIN (SELECT thread_id, COUNT(*) as count
                                        FROM post
                                        WHERE isDeleted = FALSE
                                        GROUP BY thread_id) posts ON posts.thread_id = thread.id
                            WHERE thread.id = %s;
                        '''

def get_thread_by_id(cursor, thread_id):
    cursor.execute(get_thread_by_id_query, [thread_id, ])#fetchone()
    thread = cursor.fetchone()
    return {"date": thread[0].strftime("%Y-%m-%d %H:%M:%S"),
            "dislikes": thread[1],
            "forum": thread[2],
            "id": thread[3],
            "isClosed": not not thread[4],
            "isDeleted": not not thread[5],
            "likes": thread[6],
            "message": thread[7],
            "points": thread[8],
            "posts": thread[9],
            "slug": thread[10],
            "title": thread[11],
            "user": thread[12]
           }, \
           {
           "forum": thread[13],
           "user": thread[14]
           }
