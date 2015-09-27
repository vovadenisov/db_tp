from json import dumps, loads
from django.db import DatabaseError, IntegrityError

get_user_info_query = '''SELECT about, email, id, isAnonymous, name, username
                         FROM user
                         WHERE id = %s
                      '''
get_user_followers_query = '''SELECT email
                              FROM followers INNER JOIN user
                              ON followers.follower_id = user.id
                              WHERE following_id = %s
                            '''

get_user_followings_query = '''SELECT email
                               FROM followers INNER JOIN user
                               ON followers.following_id = user.id
                               WHERE follower_id = %s
                            '''

get_user_subscriptions_query = '''SELECT thread_id
                                  FROM subscriptions
                                  WHERE user_id = %s
                               '''

def get_user_by_id(cursor, user_id):
    user = cursor.execute(get_user_info_query, [user_id]).fetchone()
    result_user = {"about": user[0],
                   "email": user[1], 
                   "followers": [],
                   "following": [],
                   "id": user[2],
                   "isAnonymous": user[3],
                   "name": user[4],
                   "subscriptions": [],
                   "username": user[5]
                   }
    followers_qs = cursor.execute(get_user_followers_query, [user_id])
    if followers_qs.rowcount:
        result_user["followers"].extend([follower[0] for follower in followers_qs.fetchall()])
    followings_qs = cursor.execute(get_user_followings_query, [user_id])
    if followings_qs.rowcount:
        result_user["followings"].extend([ffollowing[0] for following in followings_qs.fetchall()])
    subscriptions_qs = cursor.execute(get_user_subscriptions_query, [user_id])
    if subscriptions_qs.rowcount:
        result_user["subscriptions"].extend([subscription[0] for subscription in  subscriptions_qs.fetchall()])
    return result_user


