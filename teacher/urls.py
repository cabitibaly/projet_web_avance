from django.urls import path
from . import views

app_name = 'teacher'

urlpatterns = [
    path('', views.signin, name = 'signin'), # /
    path('login', views.login, name = 'login'), # /teacher/login
    path('logout', views.teacher_logout, name = 'logout'), # /teacher/logout
    path('topic', views.topic, name = 'topic'), # /teacher/topic
    path('lesson', views.lesson, name = 'lesson'), # /teacher/lesson
    path('exercice', views.exam, name = 'exercice'), # /teacher/exercice
    path('student', views.student, name = 'student'), # /teacher/student
    path('transaction', views.transaction, name = 'transaction'), # /teacher/transaction
    path('create-topic', views.create_topic, name = 'create-topic'), # /teacher/create-topic
    path('create-exercice/qcm/', views.create_qcm, name = 'create-qcm'), # /teacher/create-exercice/qcm
    path('create-exercice/question-reponse/', views.create_qr, name = 'create-qr'), # /teacher/create-exercice/question-reponse
    path('exercice/delete/<int:exercice_id>', views.delete_exercice, name = 'delete_exercice'), # /teacher/exercice/delete/id
    path('create-lesson', views.create_lesson, name = 'create-lesson'), # /teacher/create-lesson
    path('topic/delete/<int:topic_id>', views.delete_topic, name = 'delete_topic'), # /teacher/topic/delete/id
    path('topic/edit/<int:topic_id>', views.edit_topic, name = 'edit_topic'), # /teacher/topic/edit/id
    path('lesson/delete/<int:lesson_id>', views.delete_lesson, name = 'delete_lesson'), # /teacher/lesson/delete/id
    path('lesson/edit/<int:lesson_id>', views.edit_lesson, name = 'edit_lesson'), # /teacher/lesson/edit/id
]