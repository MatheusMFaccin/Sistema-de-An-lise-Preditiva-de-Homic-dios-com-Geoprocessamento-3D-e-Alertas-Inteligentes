from django.db import models


class ComparativoPrevisoes(models.Model):
    municipio = models.CharField()
    ano = models.IntegerField()
    total_vitimas_ano = models.IntegerField()
    previsao_homicidios = models.FloatField()
    previsao_min = models.FloatField()
    previsao_max = models.FloatField()
    classificacao = models.CharField()
    margem_erro_k = models.FloatField(blank=True, null=True)
    correlacao_temporal_r = models.FloatField(blank=True, null=True)
    erro_padrao_se = models.FloatField(blank=True, null=True)
    fator_penalidade_fr = models.FloatField(blank=True, null=True)
    n_anos_dados = models.IntegerField()
    id_x = models.IntegerField()
    id_y = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'comparativo_previsoes'
        unique_together = (('municipio', 'ano'),)


class DadosReaisAnuais(models.Model):
    municipio = models.CharField()
    ano = models.IntegerField()
    total_vitimas_ano = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'dados_reais_anuais'
        unique_together = (('municipio', 'ano'),)


class Datasus(models.Model):
    municipio = models.CharField()
    mes = models.CharField()
    mortes = models.IntegerField()
    ano = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'datasus'
        unique_together = (('municipio', 'ano', 'mes'),)


class Eventos(models.Model):
    uf = models.CharField()
    municipio = models.CharField()
    mes = models.CharField()
    ano = models.IntegerField()
    vitimas = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'eventos'
        unique_together = (('uf', 'municipio', 'ano', 'mes'),)


class Previsoes(models.Model):
    municipio = models.CharField()
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
