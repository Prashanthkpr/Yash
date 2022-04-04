from django.urls import path
from UserManager.views import *

app_name = 'UserManager'

urlpatterns = [
    path('login/', LoginUser.as_view(), name="login"),
    path('register/', RegisterUser.as_view(), name="register"),
    path('logout/', UserLogout.as_view(), name="logout"),
    path('list/', UsersList.as_view(), name="users-list"),
    path('update/<int:user_id>/', UsersUpdate.as_view(), name="users-update"),
    path('reset/password/<int:user_id>/', UsersPasswordReset.as_view(), name="users-password-reset")
]
