from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, UserManager
class Usuario(AbstractBaseUser):
    nome = models.CharField('Nome completo *', max_length=100)
    instituicao = models.CharField('Instituição a que pertence *', max_length=50, help_text='Registre a instituição, ou universidade, ou empresa')
    email = models.EmailField('Email', unique=True, max_length=100, db_index=True)
    celular = models.CharField('Número celular com DDD *', max_length=14, help_text="Use DDD, por exemplo 55987619832")
    cpf = models.CharField('CPF *', max_length=14, help_text='ATENÇÃO: Somente os NÚMEROS')  