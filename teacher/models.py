from django.db import models

class Matiere(models.Model):
    nom_matiere = models.CharField(max_length=20, null=False)
    img_matiere = models.ImageField(upload_to='Matiere/', default='Matiere/default-matiere.jpg')
    nombre_cours = models.IntegerField(default=0, null=True)

    LEVEL_CHOICES = [
        ('6e', '6e'),
        ('5e', '5e'),
        ('4e', '4e'),
        ('3e', '3e'),
        ('2nde', '2nde'),
        ('1ere', '1ere'),
        ('Tle', 'Tle'),
    ]
    level = models.CharField(max_length=4, choices=LEVEL_CHOICES)

class Cours(models.Model):
    de_matiere = models.ForeignKey(Matiere, on_delete = models.CASCADE)
    nom_cours = models.CharField(max_length=30, null=False)
    img_cours = models.ImageField(upload_to='Cours_img/', default='Cours_img/default-cours.jpg')
    file_cours = models.FileField(upload_to='Cours_file/')

class Exercice(models.Model):
    cours = models.ForeignKey(Cours, on_delete = models.CASCADE)
    img_exercice = models.ImageField(upload_to='exercice/', default='exercice/default-exerice.jpg')
    titre = models.CharField(max_length=50)
    type_question = models.CharField(max_length=25)
    questions = models.JSONField(default=None)
