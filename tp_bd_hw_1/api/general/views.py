from json import dumps
from django.db import connection, DatabaseError, IntegrityError, transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import codes

## CLEAR ##
clear_table_query = '''DELETE FROM {}'''
refresh_auto_increment_query = '''ALTER TABLE {} AUTO_INCREMENT = 1;'''

@csrf_exempt
def clear(request):
    cursor = connection.cursor()
    for table in ['post_hierarchy_utils', 'followers', 'subscriptions',
                  'post', 'thread', 'forum', 'user']:
        cursor.execute(clear_table_query.format(table))
        cursor.execute(refresh_auto_increment_query.format(table))
    result = {"code": codes.OK,
              "response": "OK"
             }
    cursor.close()
    return HttpResponse(dumps(result))

## STATUS ##
get_status_query = '''SELECT table_name, table_rows
                      FROM INFORMATION_SCHEMA.TABLES 
                      WHERE TABLE_SCHEMA = 'tp_hw_1'
                      AND table_name IN ('user', 'thread', 'forum', 'post')
                   '''
@csrf_exempt
def status(request):
    __cursor = connection.cursor()
    statuses_qs = __cursor.execute(get_status_query).fetchall()
    statuses = {}
    for status_ in statuses_qs:
        statuses[status_[0]] = status_[1]
    __cursor.close()
    return HttpResponse(dumps({
                          "code": codes.OK,
                          "response": statuses
                           }))


