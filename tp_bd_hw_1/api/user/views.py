from json import dumps, loads

from django.db import connection, DatabaseError, IntegrityError, transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from api.general import codes, utils as general_utils
from api.user.utils import get_user_by_id
from api.thread.utils import get_thread_by_id
from api.forum.utils import get_forum_by_id
from api.post.utils import get_post_by_id

related_functions_dict = {
                          'user': get_user_by_id,
                          'thread': get_thread_by_id,
                          'forum': get_forum_by_id
                          }

## CREATE ##
create_user_query = u''' INSERT INTO user
                         (username, about, name, email)
                         VALUES
                         (%s, %s, %s, %s);
                     '''
select_last_insert_id =  '''
                         SELECT LAST_INSERT_ID();
                         '''

update_user_query = '''UPDATE user SET isAnonymous = %s 
                       WHERE id = %s '''

@csrf_exempt                              
def create(request):
    __cursor = connection.cursor()
    try:
        json_request = loads(request.body) 
    except ValueError as value_err:
        __cursor.close()
        return HttpResponse(dumps({'code': codes.INVALID_QUERY,
                                   'response': str(value_err)}))
   
    try:
        username = json_request['username']
        about = json_request['about']
        name = json_request['name']
        email = json_request['email']
    except KeyError as key_err:
        __cursor.close()
        return HttpResponse(dumps({'code': codes.INCORRECT_QUERY,
                                   'response': 'Not found: {}'.format(str(key_err))}))    

    try:
        __cursor.execute(create_user_query, [username, about, name, email])
        __cursor.execute(select_last_insert_id, [])
    except IntegrityError as i_err:
        __cursor.close()
        print i_err
        return HttpResponse(dumps({'code': codes.USER_ALREADY_EXISTS,
                                   'response': 'user already exists'}))#'user already exists'})) 

    except DatabaseError as db_err:
        __cursor.close()
        return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                   'response': str(db_err)}))
    user_id = __cursor.fetchone()[0]
    user = {"about": about,
            "email": email,
            "id": user_id,
            "isAnonymous": False,
            "name": name,
            "username": username
             }     
    try:
        isAnonymous = json_request['isAnonymous'] 
        if not isinstance(isAnonymous, bool):
            __cursor.close()
            return HttpResponse(dumps({'code': codes.INCORRECT_QUERY,
                                       'response': 'isAnonymous flag should be bool'}))
    except KeyError:
        __cursor.close()
        return HttpResponse(dumps({'code': codes.OK,
                                   'response': user}))
    try:
        __cursor.execute(update_user_query, [isAnonymous, user_id])
    except DatabaseError as db_err: 
        __cursor.close()
        return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                   'response': str(db_err)}))
    user["isAnonymous"] = isAnonymous 
    __cursor.close()
    return HttpResponse(dumps({'code': codes.OK,
                               'response': user}))

## DETAILS ##
get_user_by_email_query = '''SELECT id FROM user
                             WHERE email = %s;
                          '''
def details(request):
    __cursor = connection.cursor()
    if request.method != 'GET':
        __cursor.close()
        return HttpResponse(dumps({'code': codes.INVALID_QUERY,
                                   'response': 'request method should be GET'}))
    email = request.GET.get('user')
    # validate user
    try:
        user_id_qs = __cursor.execute(get_user_by_email_query, [email, ])
    except DatabaseError as db_err: 
        __cursor.close()
        return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                   'response': unicode(db_err)}))

    if not __cursor.rowcount:
        __cursor.close()
        return HttpResponse(dumps({'code': codes.NOT_FOUND,
                                   'response': 'user not found'}))
    user_id = __cursor.fetchone()[0]

    try:
        user, related_ids = get_user_by_id(__cursor, user_id)
    except DatabaseError as db_err: 
        __cursor.close()
        return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                   'response': unicode(db_err)}))
    __cursor.close()
    return HttpResponse(dumps({'code': codes.OK,
                               'response': user}))    

## FOLLOW ##
create_following_relationship_query = '''INSERT INTO followers
                                         (follower_id, following_id)
                                         VALUES
                                         (%s, %s)
                                      '''

@csrf_exempt
def follow(request):
    __cursor = connection.cursor()
    try:
        json_request = loads(request.body) 
    except ValueError as value_err:
        __cursor.close()
        return HttpResponse(dumps({'code': codes.INVALID_QUERY,
                                   'response': str(value_err)}))
    
    try:
        follower = unicode(json_request['follower'])
        followee = unicode(json_request['followee'])
    except KeyError as key_err:
        __cursor.close()
        return HttpResponse(dumps({'code': codes.INCORRECT_QUERY,
                                   'response': 'Not found: {}'.format(str(key_err))}))  

    # validate users
    users = [] 
    for email in [follower, followee]:
        try:
            user_id_qs = __cursor.execute(get_user_by_email_query, [email, ]) 
        except DatabaseError as db_err: 
            __cursor.close()
            return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                       'response': unicode(db_err)}))

        if not __cursor.rowcount:
             __cursor.close()
             return HttpResponse(dumps({'code': codes.NOT_FOUND,
                                        'response': 'user with not found'}))
        user_id = __cursor.fetchone()[0]
        users.append(user_id)

    try:
        __cursor.execute(create_following_relationship_query, users)  
    except IntegrityError:
        pass
    except DatabaseError as db_err: 
        __cursor.close()
        return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                   'response': unicode(db_err)}))  
    
    try:
        user, related_ids = get_user_by_id(__cursor, users[0])
    except DatabaseError as db_err:
        __cursor.close() 
        return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                   'response': unicode(db_err)})) 
    __cursor.close()
    return HttpResponse(dumps({'code': codes.OK,
                               'response': user}))

## LIST FOLLOWERS ##
get_all_followers_query_prefix = '''SELECT user.id
                                    FROM user JOIN followers
                                    ON user.id = followers.follower_id
                                    WHERE following_id = %s 
                                 '''

def listFollowers(request):
    __cursor = connection.cursor()
    if request.method != 'GET':
        __cursor.close()
        return HttpResponse(dumps({'code': codes.INVALID_QUERY,
                                   'response': 'request method should be GET'}))
    email = request.GET.get('user')
    # validate user
    try:
        user_id_qs = __cursor.execute(get_user_by_email_query, [email, ])
    except DatabaseError as db_err: 
        __cursor.close()
        return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                   'response': unicode(db_err)}))

    if not  __cursor.rowcount:
        __cursor.close()
        return HttpResponse(dumps({'code': codes.NOT_FOUND,
                                   'response': 'user not found'}))
    user_id = __cursor.fetchone()[0]
    query = get_all_followers_query_prefix
    query_params = [user_id, ]
    since_id = general_utils.validate_id(request.GET.get('id'))
    if since_id:
        query += '''AND follower_id >= %s '''
        query_params.append(since_id)
    elif since_id == False and since_id is not None:
        __cursor.close()
        return HttpResponse(dumps({'code': codes.INCORRECT_QUERY,
                                   'response': 'incorrect since_id fromat'}))

    order = request.GET.get('order', 'desc')
    if order.lower() not in ('asc', 'desc'):
        __cursor.close()
        return HttpResponse(dumps({'code': codes.INCORRECT_QUERY,
                                   'response': 'incorrect order parameter: {}'.format(order)}))
    
    query += '''ORDER BY user.name''' + order

    limit = request.GET.get('limit')
    if limit:
        try:
            limit = int(limit)
        except ValueError:
             __cursor.close()
             return HttpResponse(dumps({'code': codes.INCORRECT_QUERY,
                                        'response': 'limit should be int'}))
        query += ''' LIMIT %s'''
        query_params.append(limit)

    try:
        user_ids_qs = __cursor.execute(query, query_params)
    except DatabaseError as db_err: 
        __cursor.close()
        return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                   'response': unicode(db_err)})) 
    
    followers = []
    if user_ids_qs:
        for user_id in __cursor.fetchall():
            try:
                user, related_ids = get_user_by_id(__cursor, user_id[0])
            except DatabaseError as db_err: 
                __cursor.close()
                return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                           'response': unicode(db_err)}))  
            followers.append(user)
    __cursor.close()
    return HttpResponse(dumps({'code': codes.OK,
                               'response': followers})) 


## LIST FOLLOWINGS ##
get_all_followings_query_prefix = '''SELECT user.id
                                     FROM user JOIN followers
                                     ON user.id = followers.following_id
                                     WHERE follower_id = %s 
                                 '''

def listFollowings(request):
    __cursor = connection.close()
    if request.method != 'GET':
        __cursor.close()
        return HttpResponse(dumps({'code': codes.INVALID_QUERY,
                                   'response': 'request method should be GET'}))
    email = request.GET.get('user')
    # validate user
    try:
        user_id_qs = __cursor.execute(get_user_by_email_query, [email, ])
    except DatabaseError as db_err: 
        __cursor.close()
        return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                   'response': unicode(db_err)}))

    if not  __cursor.rowcount:
        __cursor.close()
        return HttpResponse(dumps({'code': codes.NOT_FOUND,
                                   'response': 'user not found'}))
    user_id = __cursor.fetchone()[0]
    query = get_all_followings_query_prefix
    query_params = [user_id, ]
    since_id = general_utils.validate_id(request.GET.get('id'))
    if since_id:
        query += '''AND following_id >= %s '''
        query_params.append(since_id)
    elif since_id == False and since_id is not None:
        __cursor.close()
        return HttpResponse(dumps({'code': codes.INCORRECT_QUERY,
                                   'response': 'incorrect since_id fromat'}))

    order = request.GET.get('order', 'desc')
    if order.lower() not in ('asc', 'desc'):
        __cursor.close()
        return HttpResponse(dumps({'code': codes.INCORRECT_QUERY,
                                   'response': 'incorrect order parameter: {}'.format(order)}))
    
    query += '''ORDER BY user.name''' + order

    limit = request.GET.get('limit')
    if limit:
        try:
            limit = int(limit)
        except ValueError:
             __cursor.close()
             return HttpResponse(dumps({'code': codes.INCORRECT_QUERY,
                                        'response': 'limit should be int'}))
        query += ''' LIMIT %s'''
        query_params.append(limit)

    try:
        user_ids_qs = __cursor.execute(query, query_params)
    except DatabaseError as db_err: 
        __cursor.close()
        return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                   'response': unicode(db_err)})) 
    
    followings = []
    if user_ids_qs:
        for user_id in __cursor.fetchall():
            try:
                user, related_ids = get_user_by_id(__cursor, user_id[0])
            except DatabaseError as db_err: 
                __cursor.close()
                return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                           'response': unicode(db_err)}))  
            followings.append(user)
    return HttpResponse(dumps({'code': codes.OK,
                               'response': followings})) 

## LIST POSTS ##
get_all_user_posts_query = '''SELECT post.date, post.dislikes, forum.short_name,
                               post.id, post.isApproved, post.isDeleted,
                               post.isEdited, post.isHighlighted, post.isSpam,
                               post.likes, post.message, post.parent,
                               post.likes - post.dislikes as points, post.thread_id
                               user.email
                        FROM post JOIN user ON post.user_id = user.id
                             JOIN forum ON forum.id = post.forum_id
                        WHERE user.id = %s '''

def listPosts(request):
    __cursor = connection.cursor()
    if request.method != 'GET':
        __cursor.close()
        return HttpResponse(dumps({'code': codes.INVALID_QUERY,
                                   'response': 'request method should be GET'}))
    email = request.GET.get('user')
    # validate user
    try:
        user_id_qs = __cursor.execute(get_user_by_email_query, [email, ])
    except DatabaseError as db_err:
        __cursor.close() 
        return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                   'response': unicode(db_err)}))

    if not  __cursor.rowcount:
        __cursor.close()
        return HttpResponse(dumps({'code': codes.NOT_FOUND,
                                   'response': 'user not found'}))
    user_id = __cursor.fetchone()[0]
    query_params = [user_id, ]
    get_post_list_specified_query = get_all_user_posts_query
    since_date = general_utils.validate_date(request.GET.get('since'))
    if since_date:
        get_post_list_specified_query += '''AND post.date >= %s '''
        query_params.append(since_date)
    elif since_date == False and since_date is not None:
        __cursor.close()
        return HttpResponse(dumps({'code': codes.INCORRECT_QUERY,
                                   'response': 'incorrect since_date fromat'}))

    order = request.GET.get('order', 'desc')
    if order.lower() not in ('asc', 'desc'):
        __cursor.close()
        return HttpResponse(dumps({'code': codes.INCORRECT_QUERY,
                                   'response': 'incorrect order parameter: {}'.format(order)}))
    
    get_post_list_specified_query += '''ORDER BY post.date ''' + order

    limit = request.GET.get('limit')
    if limit:
        try:
            limit = int(limit)
        except ValueError:
             __cursor.close()
             return HttpResponse(dumps({'code': codes.INCORRECT_QUERY,
                                        'response': 'limit should be int'}))
        get_post_list_specified_query += ''' LIMIT %s'''
        query_params.append(limit)

    try:
        post_list_qs = __cursor.execute(get_post_list_specified_query, query_params)
    except DatabaseError as db_err: 
        __cursor.close()
        return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                   'response': unicode(db_err)})) 
    
    posts = []

    for post in __cursor.fetchall():
        posts.append({
            "date": post[0].strftime("%Y-%m-%d %H:%M:%S") ,
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
        })
    __cursor.close()
    return HttpResponse(dumps({'code': codes.OK,
                               'response': posts})) 

## UNFOLLOW ##
delete_following_relationship_query = '''DELETE FROM followers
                                         WHERE follower_id = %s
                                         AND following_id = %s    
                                      '''

@csrf_exempt
def unfollow(request):
    __cursor = connection.cursor()
    try:
        json_request = loads(request.body) 
    except ValueError as value_err:
        __cursor.close()
        return HttpResponse(dumps({'code': codes.INVALID_QUERY,
                                   'response': str(value_err)}))
    
    try:
        follower = unicode(json_request['follower'])
        followee = unicode(json_request['followee'])
    except KeyError as key_err:
        __cursor.close()
        return HttpResponse(dumps({'code': codes.INCORRECT_QUERY,
                                   'response': 'Not found: {}'.format(str(key_err))}))  

    # validate users
    users = [] 
    for email in [follower, followee]:
        try:
            user_id_qs = __cursor.execute(get_user_by_email_query, [email, ])
        except DatabaseError as db_err: 
            __cursor.close()
            return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                       'response': unicode(db_err)}))

        if not  __cursor.rowcount:
             __cursor.close()
             return HttpResponse(dumps({'code': codes.NOT_FOUND,
                                        'response': 'user with not found'}))
        user_id = __cursor.fetchone()[0]
        users.append(user_id)

    try:
        __cursor.execute(delete_following_relationship_query, users)  
    except DatabaseError as db_err: 
        __cursor.close()
        return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                   'response': unicode(db_err)}))  
    
    try:
        user, related_ids = get_user_by_id(__cursor, users[0])
    except DatabaseError as db_err: 
        __cursor.close()
        return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                   'response': unicode(db_err)})) 
    __cursor.close()
    return HttpResponse(dumps({'code': codes.OK,
                               'response': user}))

## UPDATE PROFILE ##
update_profile_query = '''UPDATE user
                          SET about = %,
                              name = %s,
                          WHERE email = %s;
                       '''

select_user_by_email_query = '''SELECT id FROM user
                                WHERE email = %s;'''

@csrf_exempt
def updateProfile(request):
    __cursor = connection.cursor()
    try:
        json_request = loads(request.body) 
    except ValueError as value_err:
        __cursor.close()
        return HttpResponse(dumps({'code': codes.INVALID_QUERY,
                                   'response': str(value_err)}))
    
    try:
        about = json_request['about']
        name = json_request['message']
        email = json_request['user']
    except KeyError as key_err:
        __cursor.close()
        return HttpResponse(dumps({'code': codes.INCORRECT_QUERY,
                                   'response': 'Not found: {}'.format(str(key_err))}))    


    try: 
        __cursor.execute(select_user_by_email_query, [email, ])
        if not __cursor.rowcount:
            return HttpResponse(dumps({'code': codes.INVALID_QUERY,
                                       'response': 'user does not exist'})) 
    except DatabaseError as db_err: 
        __cursor.close()
        return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                   'response': str(db_err)}))
    try:
        user_qs = __cursor.execute(update_profile_query, [about, name, email])
    except DatabaseError as db_err: 
        __cursor.close()
        return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                   'response': str(db_err)}))
 
    user_id = __cursor.fetchone()[0]
    try:
        user, related_ids = get_user_by_id(__cursor, user_id)
    except DatabaseError as db_err: 
        __cursor.close()
        return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                   'response': unicode(db_err)})) 
    __cursor.close()
    return HttpResponse(dumps({'code': codes.OK,
                               'response': user}))    

