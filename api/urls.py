from django.urls import path
from . import views
urlpatterns = [
    # In the below url we see the api overview page
    path('', views.apiOverview, name="api-overview"),
    # In the below url, if we visit "http://localhost:8000/task-detail/1/" then it shows us task 1
    path('task-detail/<str:pk>/', views.taskDetail, name="task-Detail"),
    # In the below url, if we visit "http://localhost:8000/task-create" then it shows webpage to create task POST method
    path('task-create/', views.taskCreate, name="task-Create"),
    # In the below url, we can use POST method to update task by task number "http://localhost:8000/task-update/<taskid>/" ex. taskid - 1
    path('task-update/<str:pk>/', views.taskUpdate, name="task-update"),
    # In the below url, we can use POST method to delete task "http://localhost:8000/task-delete/"
    path('task-delete/', views.taskDelete, name="task-delete"),
]
# REST API ADDED