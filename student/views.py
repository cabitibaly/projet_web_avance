from django.shortcuts import render, redirect
from django.contrib.auth import login as student_login, authenticate, get_user_model, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from student.models import Student, Otp, Score, Transaction
from teacher.models import Matiere, Cours, Exercice
from django.utils import timezone
from django.shortcuts import get_object_or_404
import random
import json
import requests
from datetime import datetime

@login_required
def index(request):
    try:
        transaction = Transaction.objects.get(user=request.user.id)
    except Transaction.DoesNotExist:
            transaction = None
    if transaction is None or transaction.status != "completed":
        return redirect('student:info')

    matieres = Matiere.objects.filter(level=request.user.level)

    if matieres.exists():
        cours_all = Cours.objects.filter(de_matiere__in=matieres)
    else:
        cours_all = None

    if cours_all.exists():
        exercices = Exercice.objects.filter(cours__in=cours_all)
    else:
        exercices = None

    context = {
        "matieres": matieres,
        "lessons": cours_all,
        "data": exercices,
        "student": request.user
    }
    return render(request, "index.html", context)

def signin(request):
    if request.method == 'POST':
        lastname = request.POST.get('lastname', '')
        firstname = request.POST.get('firstname', '')
        email = request.POST.get('email', '')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        phonenumber = request.POST.get('phonenumber', '')
        level = request.POST.get('level')
        print(level)
        if password1 != password2 :
            messages.error(request, 'Les deux mots de passe ne sont pas les mêmes.')
            return render(request, 'signin.html')

        if Student.objects.filter(email=email).exists():
            messages.error(request, 'Email déjà existants')
            return render(request, 'signin.html')
        
        if Student.objects.filter(phonenumber=phonenumber).exists():
            messages.error(request, 'Ce numéro est déjà utiliseé.')
            return render(request, 'signin.html')

        user = Student.objects.create_user(username=email, first_name=firstname, last_name=lastname, email=email, password=password1, phonenumber=phonenumber, level=level)
        user.save()
        return redirect('student:verify-email', id=user.id) 
    
    return render(request, "signin.html")

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        try:
            student = Student.objects.get(email=username)
        except Student.DoesNotExist:
            try:
                student = Student.objects.get(phonenumber=username)
            except Student.DoesNotExist:
                return redirect('student:login')
        
        try:
            transaction = Transaction.objects.get(user=student.id)
        except Transaction.DoesNotExist:
            transaction = None

        if student is not None:        
            user = authenticate(request, username=student.username, password=password)
            if user is not None:
                student_login(request, user)
                if transaction is None or transaction.status != "completed":
                    return redirect('student:info')
                
                return redirect('student:index')
        else:
            messages.warning(request, "Email, numero de telephone ou mot de passe non valide.")
            return render(request, 'login.html')
    return render(request, 'login.html')

@login_required
def logout_student(request):
    logout(request)
    return redirect('student:login')

def verify_email(request, id):
    if request.method == 'POST':
        user = get_user_model().objects.get(id=id)
        otp = Otp.objects.all().last()
        
        code_1 = request.POST.get('code-1', '')
        code_2 = request.POST.get('code-2', '')
        code_3 = request.POST.get('code-3', '')
        code_4 = request.POST.get('code-4', '')
        code_5 = request.POST.get('code-5', '')
        code_6 = request.POST.get('code-6', '')
        code = str(code_1) + str(code_2) + str(code_3) + str(code_4) + str(code_5) + str(code_6)

        if otp.code == code:
            if otp.expire_at > timezone.now():
                user.is_active = True
                user.save()

                return redirect('student:login')

            else:
                messages.warning(request, 'L\'OTP a expiré, recuperez un nouveau OTP !')
                return redirect('student:verify-email', id=user.id)
    
        else:
            messages.warning(request, 'OTP saisit invalide, entrez un OTP valide !')
            return redirect('student:verify-email', id=user.id)

    return render(request, 'verify_email.html')

def resend_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        try:
            user = get_user_model().objects.get(email=email)
            # user = get_object_or_404(Student, email = email)
            if user is not None:
                otp = Otp.objects.create(user=user, expire_at=timezone.now() + timezone.timedelta(minutes=5))
                subject = 'Email verification'
                message = f"""
                            Hi {user.username}, here is your OTP {otp.code}
                            It expires in 5 minutes, use the url below to redirect back to the website
                            Http://127.0.0.1:8000/verify-email/{user.id}
                        """
                sender = 'bitibalyclementalex@gmail.com'
                receiver = [user.email,]

                send_mail(subject, message, sender, receiver, fail_silently=False)

                messages.success(request, '')
                return redirect('student:verify-email', id=user.id)
        except Student.DoesNotExist:
            messages.warning(request, 'The email does not exist in the database')
            return redirect('student:resend-otp')
    
    return render(request, 'resend.html')

@login_required
def matieres(request):
    try:
        transaction = Transaction.objects.get(user=request.user.id)
    except Transaction.DoesNotExist:
            transaction = None
    
    if transaction is None or transaction.status != "completed":
        return redirect('student:info')
     
    context = {
        "data": Matiere.objects.filter(level=request.user.level),
        "student": request.user
    }
    return render(request, 'matieres.html', context)

@login_required
def cours(request):
    try:
        transaction = Transaction.objects.get(user=request.user.id)
    except Transaction.DoesNotExist:
            transaction = None
    
    if transaction is None or transaction.status != "completed":
        return redirect('student:info')

    matieres = Matiere.objects.filter(level=request.user.level)

    if matieres.exists():
        cours = Cours.objects.filter(de_matiere__in=matieres)
    else:
        cours = None
    context = {
        "data": cours,
        "student": request.user
    }
    return render(request, 'cours.html', context)

@login_required
def exercices(request):
    try:
        transaction = Transaction.objects.get(user=request.user.id)
    except Transaction.DoesNotExist:
            transaction = None
    
    if transaction is None or transaction.status != "completed":
        return redirect('student:info')

    matieres = Matiere.objects.filter(level=request.user.level)
    # matiere = matieres[0].id if matieres else None
    if matieres.exists():
        cours_all = Cours.objects.filter(de_matiere__in=matieres)
    else:
        cours_all = None

    if cours_all.exists():
        exercices = Exercice.objects.filter(cours__in=cours_all)
    else:
        exercices = None

    context = {
        "data": exercices,
        "student": request.user
    }
    return render(request, 'exercice.html', context)

@login_required
def show_matiere(request, matiere_id):
    try:
        transaction = Transaction.objects.get(user=request.user.id)
    except Transaction.DoesNotExist:
            transaction = None
    
    if transaction is None or transaction.status != "completed":
        return redirect('student:info')

    context = {
        "data": Cours.objects.filter(de_matiere = matiere_id),
        "matiere": Matiere.objects.get(id=matiere_id),
        "student": request.user
    }
    return render(request, 'show_matiere.html', context)

@login_required
def show_cours(request, cours_id):
    try:
        transaction = Transaction.objects.get(user=request.user.id)
    except Transaction.DoesNotExist:
            transaction = None
    
    if transaction is None or transaction.status != "completed":
        return redirect('student:info')

    cours = Cours.objects.get(id=cours_id)
    cours_all = Cours.objects.filter(id=cours_id)
    exercices = Exercice.objects.filter(cours__in=cours_all)
    context = {
        "cours": cours,
        "data": exercices,
        "student": request.user
    }

    if cours.file_cours.name.endswith(".pdf"):
        return render(request, "cours_pdf.html", context)
    elif cours.file_cours.name.endswith(".mp4"):
        return render(request, "cours_video.html", context)

    return redirect('student:cours')

@login_required
def show_exercice(request, exercice_id):
    try:
        transaction = Transaction.objects.get(user=request.user.id)
    except Transaction.DoesNotExist:
            transaction = None
    
    if transaction is None or transaction.status != "completed":
        return redirect('student:info')

    exercice = Exercice.objects.get(id=exercice_id)

    context = {
        "data": exercice,
        "student": request.user
    }

    if exercice.type_question == 'qcm':
        return render(request, "exercice_qcm.html", context)
    elif exercice.type_question == 'qr':
        return render(request, "exercice_qr.html", context)
    
    return redirect('student:exercices')

@login_required
def score(request, exercice_id):
    try:
        transaction = Transaction.objects.get(user=request.user.id)
    except Transaction.DoesNotExist:
            transaction = None
    
    if transaction is None or transaction.status != "completed":
        return redirect('student:info')
    
    if request.method == 'POST':
        user_score = request.POST.get('user-score')
        print(user_score)
        student = Student.objects.get(id=request.user.id)
        student.point += int(user_score)
        student.save()
        if student.point > 30 and student.point <= 80:
            student.niveau = 'Moyen'
        elif student.point > 80:
            student.niveau = 'Pro'

        exercice = Exercice.objects.get(id=exercice_id)
        score = Score.objects.create(user=student, exercice=exercice, score=user_score)
        score.save()
        return redirect('student:cours')
    return render(request, "cours.html")

@login_required
def student_profile(request):
    try:
        transaction = Transaction.objects.get(user=request.user.id)
    except Transaction.DoesNotExist:
            transaction = None
    
    if transaction is None or transaction.status != "completed":
        return redirect('student:info')

    student = Student.objects.get(id=request.user.id)

    if request.method == 'POST':
        lastname = request.POST.get('lastname', '')
        firstname = request.POST.get('firstname', '')
        email = request.POST.get('email', '')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        phonenumber = request.POST.get('phonenumber', '')
        level = request.POST.get('level', '')
        img = request.FILES.get('img')

        if password1 == "" and img is not None:
            student.username = email
            student.last_name = lastname
            student.first_name = firstname
            student.phonenumber = phonenumber
            student.level = level
            student.image = img
            student.save()
            return render(request, 'profile.html', {"data": student})
        elif password1 == "":
            student.username = email
            student.last_name = lastname
            student.first_name = firstname
            student.phonenumber = phonenumber
            student.level = level
            student.save()
            return render(request, 'profile.html', {"data": student})
            
        
        user = authenticate(request, username=email, password=password1)

        if user is None :
            print('Ancienne mot de passe incorrecte.')
            messages.error(request, 'Ancienne mot de passe incorrecte.')
            return render(request, 'profile.html', {"data": student})

        if img == "" and password2 != "":
            print('vide')
            student.set_password(password2)
            student.username = email
            student.last_name = lastname
            student.first_name = firstname
            student.phonenumber = phonenumber
            student.level = level
            student.save()
            update_session_auth_hash(request, user)
            return render(request, 'profile.html', {"data": student})
    
        student.set_password(password2)
        student.username = email
        student.last_name = lastname
        student.first_name = firstname
        student.phonenumber = phonenumber
        student.level = level
        # student.image = img
        student.save()
        update_session_auth_hash(request, user)
        return render(request, 'profile.html', {"data": student})

    return render(request, 'profile.html', {"data": student})

@login_required
def payement(request):
    if Transaction.objects.filter(user=request.user.id).exists():
        Transaction.objects.get(user=request.user.id).delete()
    transac_id = f'TRANS{random.randint(0, 9999)}{datetime.now().strftime("%Y%m%d%H%M%S")}'
    user = request.user
    response = redirection_payement(transac_id)


    if response.get('response_code') == '00':
        token = response.get("token")
        redirect_url = response.get("response_text")

        Transaction.objects.create(
            user=user,
            transID=transac_id,
            status="pending",
            token=token 
        )

        request.session['transaction_id'] = transac_id
        return redirect(redirect_url)
    else:
        
        return render(request, 'cancel.html')

def redirection_payement(trans_id):
    url = "https://app.ligdicash.com/pay/v01/redirect/checkout-invoice/create"
    headers = {
        "Apikey": "MAGPMLT3QFJLIPUDN",
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZF9hcHAiOjE1MDA5LCJpZF9hYm9ubmUiOjg5OTQyLCJkYXRlY3JlYXRpb25fYXBwIjoiMjAyNC0wNC0wOCAwODozMjoyNCJ9.NRcyHfFO8OyaXOaklZ2DJ2Arf-gV8OXGfMIELQzdw88",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "commande": {
            "invoice": {
                "items": [
                    {
                        "name": "abonnement",
                        "description": "abonnement a edumin",
                        "quantity": 1,
                        "unit_price": "10",
                        "total_price": "10"
                    }
                ],
                "total_amount": "10",
                "devise": "XOF",
                "description": "abonnement a edumin",
                "customer": "",
                "customer_firstname": "Prenom du client",
                "customer_lastname": "Nom du client",
                "customer_email": "erasuamert@gmail.com"
            },
            "store": {
                "name": "webapp",
                "website_url": "https://appweb.com"
            },
            "actions": {
                "cancel_url": "http://127.0.0.1:8000/cancel/",
                "return_url": "http://localhost:8000/success/",
                "callback_url": "http://localhost:8000/success/"
            },
            "custom_data": {
                "transaction_id": trans_id
            }
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
    return response.json()

@login_required
def cancel(request):
    return render(request, 'cancel.html')

@login_required
def info_payement(request):
    return render(request, 'payement.html')

@login_required
def success(request):
    transaction_id = request.session.get('transaction_id')
    if transaction_id:
        payment = Transaction.objects.get(transID=transaction_id)
        payment_data = check_payment_status(payment.token)

        if payment_data.get("status") == "completed":  
            payment.status = "completed"
            payment.save()

            return redirect('student:index')
        else:
            return redirect('student:cancel')
    else:
        messages.error(request, 'Erreur de transaction. Veuillez réessayer.')
        return redirect('student:info')
    
def check_payment_status(token):
    url = f"https://app.ligdicash.com/pay/v01/redirect/checkout-invoice/confirm/?invoiceToken={token}"
    headers = {
        "Apikey": "MAGPMLT3QFJLIPUDN",
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZF9hcHAiOjE1MDA5LCJpZF9hYm9ubmUiOjg5OTQyLCJkYXRlY3JlYXRpb25fYXBwIjoiMjAyNC0wNC0wOCAwODozMjoyNCJ9.NRcyHfFO8OyaXOaklZ2DJ2Arf-gV8OXGfMIELQzdw88",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as errh:
        return {"error": "HTTP Error", "message": str(errh)}
    except requests.exceptions.RequestException as err:
        return {"error": "Request Exception", "message": str(err)}
