from django.urls import path
from . import views

app_name = "student"

urlpatterns = [
    path('home/', views.index, name = 'index'), # /
    path('', views.signin, name = 'signin'), # /signin
    path('login/', views.login, name = 'login'), # /login    
    path('logout/', views.logout_student, name = 'logout'), # /logout    
    path('profile/', views.student_profile, name = 'profile'), # /profile    
    path('verify-email/<slug:id>', views.verify_email, name = 'verify-email'), # /verify-email/:username
    path('resend-otp/', views.resend_otp, name = 'resend-otp'), # /resend-otp  
    path('matiere/', views.matieres, name = 'matieres'), # /matiere
    path('cours/', views.cours, name = 'cours'), # /cours
    path('cours/<int:cours_id>', views.show_cours, name = 'show-cours'), # /cours/id
    path('exercice/', views.exercices, name = 'exercices'), # /exercice
    path('exercice/<int:exercice_id>', views.show_exercice, name = 'show-exercice'), # /exercice/id
    path('matiere/<int:matiere_id>', views.show_matiere, name = 'show-matiere'), # /matiere/id
    path('score/<int:exercice_id>', views.score, name = 'score'), # /score/id
    path('payement/', views.payement, name = 'payement'), # /payement
    path('payement/info', views.info_payement, name = 'info'), # /payement/info
    path('success/', views.success, name = 'success'), # /success
    path('cancel/', views.cancel, name = 'cancel'), # /cancel   
]