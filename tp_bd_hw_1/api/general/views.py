from json import dumps
from django.http import HttpResponse

from general import codes

__cursor = connection.cursor()

## CLEAR ##
clear_database_query = '''DELETE FROM post_hierarchy_utils;
                          DELETE FROM followers;
                          DELETE FROM subscriptions;
                          DELETE FROM post;
                          DELETE FROM thread;
                          DELETE FROM forum;
                          DELETE FROM user;
                       '''
def clear(request):
    __cursor.execute(clear_database_query)
    result = {"code": codes.OK,
              "response": "OK"
             }
    return HttpResponse(dumps(result))

## STATUS ##
get_status_query = '''SELECT table_name, table_rows
                      FROM INFORMATION_SCHEMA.TABLES 
                      WHERE TABLE_SCHEMA = 'tp_hw_1'
                      AND table_name IN ('user', 'thread', 'forum', 'post')
                   '''

def status(request):
    statuses_qs = __cursor.execute(get_status_query).fetchall()
    statuses = {}
    for status in statuses_qs:
        statuses[status[0]] = status[1]
    return HttpResponse(dumps({
                          "code": codes.OK,
                          "response": statuses
                           }))


