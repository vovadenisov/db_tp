from json import dumps
from django.db import connection, DatabaseError, IntegrityError, transaction
from django.http import HttpResponse

from general import codes, utils as general_utils
from user.utils import get_user_by_id
from thread.utils import get_thread_by_id
from .utils import get_forum_by_id

__cursor = connection.cursor()

## CREATE ##
create_forum_query = '''INSERT INTO forum
                        (name, short_name, user_id)
                        VALUES
                        (%s, %s, %s);
                        SELECT LAST_INSERT_ID();
                     '''
get_user_by_email_query = '''SELECT id FROM user
                             WHERE email = %s;
                          '''

get_forum_by_short_name_query = '''SELECT id FROM forum
                                   WHERE short_name = %s;
                                '''

get_thread_by_id_query = '''SELECT id FROM thread
                            WHERE id = %s;
                         '''

get_post_by_id_and_update_query = '''UPDATE post
                                     SET child_posts_count = child_posts_count + 1
                                     WHERE id = %s;
                                     SELECT id, child_posts_count, hierarchy_id FROM post
                                     WHERE id = %s;
                                  '''

get_max_post_and_update_query = '''UPDATE post_hierarchy_utils
                                   SET head_posts_number = head_posts_number + 1
                                   WHERE forum_id = %s;
                                   SELECT head_posts_number
                                   FROM post_hierarchy_utils
                                   WHERE forum_id = %s; 
                                '''

get_max_post_and_insert_query = '''INSERT INTO post_hierarchy_utils
                                   (forum_id, head_posts_number)
                                   VALUES
                                   (%s, 1);
                                   SELECT head_posts_number
                                   FROM post_hierarchy_utils
                                   WHERE forum_id = %s; 
                                '''
create_post_base_query = '''INSERT INTO post 
                            (name, short_name, user_id)
                            VALUES
                            (%s, %s, %s);
                            SELECT LAST_INSERT_ID();
                         '''#TODO
def create(request):
    try:
        json_request = loads(request.body) 
    except ValueError as value_err:
        return HttpResponse(dumps({'code': codes.INVALID_QUERY,
                                   'response': str(value_err)}))
    
    try:
        date = json_request['date']
        thread_id = json_request['thread']
        message = json_request['message']
        forum = json_request['forum']
        email = json_request['user']
    except KeyError as key_err:
        return HttpResponse(dumps({'code': codes.INCORRECT_QUERY,
                                   'response': 'Not found: {}'.format(str(key_err))}))    
    # validate user
    try:
        user_id_qs = __cursor.execute(get_user_by_email_query, [email, ])  
    except DatabaseError as db_err: 
        return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                   'response': str(db_err)}))

    if not user_id_qs.rowcount:
        return HttpResponse(dumps({'code': codes.NOT_FOUND,
                                   'response': 'user not found'}))
    user_id = user_id_qs.fetchone()[0]
    
    # validate forum
    try:
        forum_id_qs = __cursor.execute(get_forum_by_short_name_query, [forum, ])  
    except DatabaseError as db_err: 
        return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                   'response': str(db_err)}))

    if not forum_id_qs.rowcount:
        return HttpResponse(dumps({'code': codes.NOT_FOUND,
                                   'response': 'forum not found'}))
    forum_id = forum_id_qs.fetchone()[0]

    #validate thread
    try:
        thread_id_qs = __cursor.execute(get_thread_by_id_query, [thread_id, ])  
    except DatabaseError as db_err: 
        return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                   'response': str(db_err)}))

    if not thread_id_qs.rowcount:
        return HttpResponse(dumps({'code': codes.NOT_FOUND,
                                   'response': 'thread not found'}))
    #validate date
    date = general_utils.validate_date(date)
    if not date:
        return HttpResponse(dumps({'code': codes.INCORRECT_QUERY,
                                   'response': 'incorrect date fromat'}))
    #validate message
    if not message:
        return HttpResponse(dumps({'code': codes.INCORRECT_QUERY,
                                   'response': 'message should not be empty'}))

    parent_id = request.GET.get('parent')
    with transaction.atomic():
        if parent_id:
            try:
                post_qs = __cursor.execute(get_post_by_id_and_update_query, [parent_id, parent_id])  
            except DatabaseError as db_err: 
                return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                           'response': str(db_err)}))

            if not post_qs.rowcount:
                return HttpResponse(dumps({'code': codes.NOT_FOUND,
                                           'response': 'parent post not found'}))
            post = post_qs.fetchone()
            hierarchy_id = post[2] + str(post[1]) + '/'    
        else:
            try:
                max_post_qs = __cursor.execute(get_max_post_and_update_query, [parent_id, parent_id])  
            except DatabaseError as db_err: 
                return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                           'response': str(db_err)}))

            if not max_post_qs.rowcount:
                max_post_qs = __cursor.execute(get_max_post_and_insert_query, [parent_id, parent_id])  

            post = max_post_qs.fetchone()
            hierarchy_id = str(post[0]) + '/'
        ## TODO: INSERT  

    try:
        forum_id_qs = __cursor.execute(create_forum_query, [name, short_name, user_id]).fetchone()
        return HttpResponse(dumps({'code': codes.OK,
                                   'response': {
                                        'id': forum_id_qs[0],
                                        'name': name,
                                        'short_name': short_name,
                                        'user': email
                                         }}))
    except IntegrityError:
        existed_forum = __cursor.execute(get_forum_by_short_name_query, [short_name]).fetchone()
        return HttpResponse(dumps({'code': codes.OK,
                                   'response': {
                                        'id': existed_forum[0],
                                        'name': existed_forum[1],
                                        'short_name': existed_forum[2],
                                        'user': existed_forum[3]
                                         }}))
    except DatabaseError as db_err: 
        return HttpResponse(dumps({'code': codes.UNKNOWN_ERR,
                                   'response': str(db_err)}))


def details(request):
    result = {}
    return HttpResponse(dumps(result))

def list_posts(request):
    result = {}
    return HttpResponse(dumps(result))

def remove(request):
    result = {}
    return HttpResponse(dumps(result))

def restore(request):
    result = {}
    return HttpResponse(dumps(result))

def update(request):
    result = {}
    return HttpResponse(dumps(result))

def vote(request):
    result = {}
    return HttpResponse(dumps(result))
