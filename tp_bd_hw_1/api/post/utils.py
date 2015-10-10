from json import dumps, loads
from django.db import DatabaseError, IntegrityError



get_post_by_id_query = ''' SELECT post.date, post.dislikes, forum.short_name, post.id,
                                  post.isApproved, post.isDeleted, post.isEdited, post.isHighlighted, 
                                  post.isSpam, post.likes, post.message, post.parent, 
                                  post.likes - post.dislikes as points, post.thread_id, user.email,
                                  post.forum_id, post.thread_id, post.user_id
                           FROM post INNER JOIN user
                           ON post.user_id = user.id
                           INNER JOIN forum on forum.id = post.forum_id
                           WHERE post.id = %s;
                        '''

def get_post_by_id(cursor, post_id):
    post_qs = cursor.execute(get_post_by_id_query, [post_id,])
    post = post_qs.fetchone()
    return {
        "date": post[0],
        "dislikes": post[1],
        "forum": post[2],
        "id": post[3],
        "isApproved": post[4],
        "isDeleted": post[5],
        "isEdited": post[6],
        "isHighlighted": post[7],
        "isSpam": post[8],
        "likes": post[9],
        "message": post[10],
        "parent": post[11],
        "points": post[12],
        "thread": post[13],
        "user": post[14]
        }, \
        {
         "forum": post[15],
         "thread": post[16],
         "user": post[17]
         }
