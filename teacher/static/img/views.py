from django.shortcuts import render, redirect
from django.contrib import messages
from teacher.models import Matiere, Cours, Exercice
from django.conf import settings
import os

# Matiere

def create_topic(request):
    if request.method == 'POST':
        topic_name = request.POST.get('matiere', '')
        topic_image = request.FILES.get('image')
        topic_level = request.POST.get('level')

        if Matiere.objects.filter(nom_matiere=topic_name).exists():
            messages.error(request, 'Topic already exists.')
            return render(request, 'create_topic.html')
        
        if topic_image == "":
            matiere = Matiere.objects.create(nom_matiere=topic_name, level=topic_level)
            matiere.save()
            return redirect('teacher:topic')

        matiere = Matiere.objects.create(nom_matiere=topic_name, level=topic_level, img_matiere=topic_image)
        matiere.save()
        return redirect('teacher:topic')
    return render(request, "create_topic.html")

def topic(request):
    context = {'matieres' : Matiere.objects.all()}
    return render(request, "topics.html", context)

def delete_topic(request, topic_id):
    matiere = Matiere.objects.filter(id=topic_id)
    matiere.delete()
    context = {'matieres' : Matiere.objects.all()}
    return render(request, "topics.html", context)

def edit_topic(request, topic_id):
    matiere = Matiere.objects.get(id=topic_id)
    context = {"matiere": matiere}
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

def create_lesson(request):
    if request.method == 'POST':
        lesson_name = request.POST.get('lesson-name', '')
        lesson_topic = request.POST.get('topics', '')
        lesson_image = request.FILES.get('lesson-image')    
        lesson_file = request.FILES.get('file')

        if Cours.objects.filter(nom_cours=lesson_name).exists():
            messages.error(request, 'Ce cours existe déjà.')
            return render(request, 'create_lesson.html')

        matiere = Matiere.objects.get(nom_matiere=lesson_topic)
        matiere.nombre_cours += 1
        matiere.save()
        cours = Cours.objects.create(de_matiere=matiere, nom_cours=lesson_name, img_cours=lesson_image, file_cours=lesson_file)
        cours.save()
        return redirect('teacher:lesson')
    
    topics = Matiere.objects.all()
    context = {'topics': topics}
    return render(request, 'create_lesson.html', context)

def lesson(request):
    context = {"lessons": Cours.objects.all()}
    return render(request, "lessons.html", context)

def delete_lesson(request, lesson_id):
    lesson = Cours.objects.filter(id=lesson_id)
    lesson.delete()
    context = {'lessons' : Cours.objects.all()}
    return render(request, "lessons.html", context)

def edit_lesson(request, lesson_id):
    lesson = Cours.objects.get(id=lesson_id)
    context = {"lesson": lesson, "topics": Matiere.objects.all()}
    if request.method == 'POST':
        lesson_name = request.POST.get('lesson-name', '')
        lesson_topic = request.POST.get('topics', '')
        lesson_image = request.FILES.get('lesson-image')    
        lesson_file = request.FILES.get('file')
        
        if lesson_image == None and lesson_file == None:
            lesson.nom_cours = lesson_name
            matiere = Matiere.objects.get(nom_matiere=lesson_topic)
            lesson.de_matiere = matiere
            lesson.save()
            return redirect('teacher:lesson')
        
        lesson.nom_cours = lesson_name
        lesson.img_cours = lesson_image
        lesson.file_cours = lesson_file
        matiere = Matiere.objects.get(nom_matiere=lesson_topic)
        lesson.de_matiere = matiere
        lesson.save()
        return redirect('teacher:lesson')
    
    return render(request, 'edit_lesson.html', context)

#exercice

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
                # print(choix_possible)
                # print(request.POST.get(correct))
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
    context = {"lessons": cours}
    return render(request, 'create_qcm.html', context)

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
    context = {"lessons": cours}
    return render(request, 'question_reponse.html', context)

def exam(request):
    context = {'exercices': Exercice.objects.all()}
    return render(request, "exams.html", context)

def delete_exercice(request, exercice_id):
    exercice = Exercice.objects.filter(id=exercice_id)
    exercice.delete()
    context = {'exercices': Exercice.objects.all()}
    return render(request, "exams.html", context)


# Chat

def chat(request):
    context = {}
    return render(request, "chat.html")
