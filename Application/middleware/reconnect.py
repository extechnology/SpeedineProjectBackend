# from django.db import connection
# from MySQLdb import OperationalError

# class KeepMySQLAliveMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         try:
#             connection.cursor()  # check connection
#         except OperationalError:
#             connection.close()   # reconnect
#         return self.get_response(request)
