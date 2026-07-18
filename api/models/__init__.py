# models/__init__.py
# Importar na ordem correta: pais antes dos filhos
from models.municipio import Municipio
from models.evento import Evento
from models.datasus import Datasus
from models.previsao import Previsao
from models.dados_reais import EventosTotaisAnuais
from models.ComparativoPrevisao import ComparativoPrevisao
