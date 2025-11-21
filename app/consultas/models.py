# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AlembicVersion(models.Model):
    version_num = models.CharField(primary_key=True, max_length=32)

    class Meta:
        managed = False
        db_table = 'alembic_version'


class ComparativoPrevisoes(models.Model):
    previsao = models.ForeignKey('Previsoes', models.DO_NOTHING)
    dado_real = models.ForeignKey('DadosReaisAnuais', models.DO_NOTHING, blank=True, null=True)
    municipio = models.ForeignKey('Municipios', models.DO_NOTHING)
    ano = models.IntegerField()
    total_vitimas_ano = models.IntegerField(blank=True, null=True)
    previsao_homicidios = models.FloatField()
    previsao_min = models.FloatField()
    previsao_max = models.FloatField()
    classificacao = models.CharField()
    margem_erro_k = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comparativo_previsoes'
        unique_together = (('municipio', 'ano'),)


class DadosReaisAnuais(models.Model):
    municipio = models.ForeignKey('Municipios', models.DO_NOTHING)
    ano = models.IntegerField()
    total_vitimas_ano = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'dados_reais_anuais'
        unique_together = (('municipio', 'ano'),)


class Datasus(models.Model):
    municipio = models.ForeignKey('Municipios', models.DO_NOTHING)
    ano = models.IntegerField()
    mes = models.IntegerField()
    mortes = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'datasus'
        unique_together = (('municipio', 'ano', 'mes'),)


class Eventos(models.Model):
    municipio = models.ForeignKey('Municipios', models.DO_NOTHING)
    mes = models.IntegerField()
    ano = models.IntegerField()
    vitimas = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'eventos'
        unique_together = (('municipio', 'ano', 'mes'),)


class Municipios(models.Model):
    nome = models.CharField()
    uf = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'municipios'


class Previsoes(models.Model):
    municipio = models.ForeignKey(Municipios, models.DO_NOTHING)
    ano_previsao = models.IntegerField()
    previsao_homicidios = models.IntegerField()
    previsao_min = models.IntegerField()
    previsao_max = models.IntegerField()
    n_anos_dados = models.IntegerField()
    margem_erro_k = models.FloatField(blank=True, null=True)
    correlacao_temporal_r = models.FloatField(blank=True, null=True)
    erro_padrao_se = models.FloatField(blank=True, null=True)
    fator_penalidade_fr = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'previsoes'
        unique_together = (('municipio', 'ano_previsao'),)
