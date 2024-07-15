from django.shortcuts import render, redirect
from django.contrib import messages
from teacher.models import Matiere, Cours, Exercice
from student.models import Student, Transaction
from django.contrib.auth import login as teacher_login, authenticate, logout
from django.contrib.auth.decorators import login_required

# Enseignant

def signin(request):
    if request.method == 'POST':
        lastname = request.POST.get('last_name', '')
        firstname = request.POST.get('first_name', '')
        email = request.POST.get('email', '')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if password1 != password2 :
            messages.error(request, 'Les deux mots de passe ne sont pas les mêmes.')
            return render(request, 'teacher_signin.html')

        if Student.objects.filter(email=email).exists():
            messages.error(request, 'Email déjà existants')
            return render(request, 'teacher_signin.html')

        user = Student.objects.create_user(username=email, is_active=True, first_name=firstname, last_name=lastname, email=email, password=password1, role='teacher')
        user.save()

        return redirect('teacher:login')
    
    return render(request, "teacher_signin.html")

def login(request):
    if request.method == 'POST':
        username = request.POST.get('email', '')
        password = request.POST.get('password', '')

        student = Student.objects.get(email=username)
        
        if student is not None:        
            user = authenticate(request, username=student.username, password=password)
            if user is not None and user.role == 'teacher':
                teacher_login(request, user)
                return redirect('teacher:topic')
        else:
            messages.warning(request, "Email, numero de telephone ou mot de passe non valide.")
            return render(request, 'teacher_login.html')
    return render(request, 'teacher_login.html')

@login_required
def teacher_logout(request):
    logout(request)
    return redirect('teacher:login')

# Matiere

@login_required
def create_topic(request):
    if request.user.role == 'teacher':
        if request.method == 'POST':
            topic_name = request.POST.get('matiere', '')
            topic_image = request.FILES.get('image')
            topic_level = request.POST.get('level')        
            
            if topic_image == "":
                matiere = Matiere.objects.create(nom_matiere=topic_name, level=topic_level)
                matiere.save()
                return redirect('teacher:topic')

            matiere = Matiere.objects.create(nom_matiere=topic_name, level=topic_level, img_matiere=topic_image)
            matiere.save()
            return redirect('teacher:topic')
        return render(request, "create_topic.html")
    
    return redirect('teacher:login')

@login_required
def topic(request):
    if request.user.role == 'teacher':
        context = {'matieres' : Matiere.objects.all(), "teacher": request.user}
        return render(request, "topics.html", context)
    return redirect('teacher:login')

@login_required
def delete_topic(request, topic_id):
    matiere = Matiere.objects.filter(id=topic_id)
    matiere.delete()
    context = {'matieres' : Matiere.objects.all(), "teacher": request.user}
    return render(request, "topics.html", context)

@login_required
def edit_topic(request, topic_id):
    matiere = Matiere.objects.get(id=topic_id)
    context = {"matiere": matiere, "teacher": request.user}
    if request.method == 'POST':
        topic_name = request.POST.get('matiere', '')
        topic_image = request.FILES.get('image')
        topic_level = request.POST.get('level')
        
        if topic_image == None:
            matiere.nom_matiere = topic_name
            matiere.level = topic_level
            matiere.save()
            return redirect('teacher:topic')
        
        matiere.nom_matiere = topic_name
        matiere.level = topic_level
        matiere.img_matiere = topic_image
        matiere.save()
        return redirect('teacher:topic')
    
    return render(request, 'edit_topic.html', context)

# Leçon

@login_required
def create_lesson(request):
    if request.method == 'POST':
        lesson_name = request.POST.get('lesson-name', '')
        lesson_topic = request.POST.get('topics', '')
        lesson_image = request.FILES.get('lesson-image')    
        lesson_file = request.FILES.get('file')

        if Cours.objects.filter(nom_cours=lesson_name).exists():
            messages.error(request, 'Ce cours existe déjà.')
            return render(request, 'create_lesson.html')

        matiere = Matiere.objects.get(id=lesson_topic)
        matiere.nombre_cours += 1
        matiere.save()
        cours = Cours.objects.create(de_matiere=matiere, nom_cours=lesson_name, img_cours=lesson_image, file_cours=lesson_file)
        cours.save()
        return redirect('teacher:lesson')
    
    topics = Matiere.objects.all()
    context = {'topics': topics, "teacher": request.user}
    return render(request, 'create_lesson.html', context)

@login_required
def lesson(request):
    context = {"lessons": Cours.objects.all(), "teacher": request.user}
    return render(request, "lessons.html", context)

@login_required
def delete_lesson(request, lesson_id):
    lesson = Cours.objects.filter(id=lesson_id)
    lesson.delete()
    context = {'lessons' : Cours.objects.all(), "teacher": request.user}
    return render(request, "lessons.html", context)

@login_required
def edit_lesson(request, lesson_id):
    lesson = Cours.objects.get(id=lesson_id)
    context = {"lesson": lesson, "topics": Matiere.objects.all(), "teacher": request.user}
    if request.method == 'POST':
        lesson_name = request.POST.get('lesson-name', '')
        lesson_topic = request.POST.get('topics', '')
        lesson_image = request.FILES.get('lesson-image')    
        lesson_file = request.FILES.get('file')
        
        if lesson_image == None and lesson_file == None:
            lesson.nom_cours = lesson_name
            matiere = Matiere.objects.get(id=lesson_topic)
            lesson.de_matiere = matiere
            lesson.save()
            return redirect('teacher:lesson')
        elif lesson_image is None:
            lesson.nom_cours = lesson_name
            lesson.file_cours = lesson_file
            matiere = Matiere.objects.get(id=lesson_topic)
            lesson.de_matiere = matiere
            lesson.save()
            return redirect('teacher:lesson')
        elif lesson_file is None:
            lesson.nom_cours = lesson_name
            lesson.img_cours = lesson_image
            matiere = Matiere.objects.get(id=lesson_topic)
            lesson.de_matiere = matiere
            lesson.save()
            return redirect('teacher:lesson')
        
        lesson.nom_cours = lesson_name
        lesson.img_cours = lesson_image
        lesson.file_cours = lesson_file
        matiere = Matiere.objects.get(id=lesson_topic)
        lesson.de_matiere = matiere
        lesson.save()
        return redirect('teacher:lesson')
    
    return render(request, 'edit_lesson.html', context)

#exercice

@login_required
def create_qcm(request):
    if request.method == 'POST':
        titre_exo = request.POST.get('exercice-name')
        lesson = request.POST.get('cours')
        nb_question = request.POST.get('questions')
        img = request.FILES.get('exercice-image')
        questions = []
        for i in range(int(nb_question)):
            enonce = 'enonce-' + str(i+1)
            text = request.POST.get(enonce)
            choix = []
            for j in range(3):
                choice = enonce + '-' + 'choix-' + str(j+1)
                correct = enonce + '-' + 'correcte-' + str(j+1)    
                print(correct)            
                choix_possible = request.POST.get(choice)
                est_correct = request.POST.get(correct) == 'on'
                choix.append({"choix": choix_possible, "est_correcte": est_correct})
            
            questions.append({
                "text": text,
                "choix": choix
            })

        find_lesson = Cours.objects.get(nom_cours=lesson)
        exam = Exercice.objects.create(cours=find_lesson, img_exercice=img, titre=titre_exo, type_question="qcm", questions=questions)
        exam.save()
        return redirect('teacher:exercice')
    cours = Cours.objects.all()
    context = {"lessons": cours, "teacher": request.user}
    return render(request, 'create_qcm.html', context)

@login_required
def create_qr(request):
    if request.method == 'POST':
        titre_exo = request.POST.get('exercice-name')
        nb_question = request.POST.get('questions')        
        lesson = request.POST.get('cours')
        img = request.FILES.get('exercice-image')
        questions = []
        for i in range(int(nb_question)):
            enonce = 'enonce-' + str(i+1)
            text = request.POST.get(enonce)
            rep = enonce + '-' + 'reponse'
            reponse = request.POST.get(rep)
            
            questions.append({
                "text": text,
                "reponse": reponse
            })

        find_lesson = Cours.objects.get(nom_cours=lesson)
        exam = Exercice.objects.create(cours=find_lesson, img_exercice=img, titre=titre_exo, type_question='qr', questions=questions)
        exam.save()
        return redirect('teacher:exercice')
        
    cours = Cours.objects.all()
    context = {"lessons": cours, "teacher": request.user}
    return render(request, 'question_reponse.html', context)

@login_required
def exam(request):
    context = {'exercices': Exercice.objects.all(), "teacher": request.user}
    return render(request, "exams.html", context)

@login_required
def delete_exercice(request, exercice_id):
    exercice = Exercice.objects.filter(id=exercice_id)
    exercice.delete()
    context = {'exercices': Exercice.objects.all(), "teacher": request.user}
    return render(request, "exams.html", context)


# Élèves

@login_required
def student(request):
    context = {"data": Student.objects.filter(role='student'), "teacher": request.user}
    return render(request, "student.html", context)

@login_required
def transaction(request):
    context = {"data": Transaction.objects.all(), "teacher": request.user}
    return render(request, "transaction.html", context)
