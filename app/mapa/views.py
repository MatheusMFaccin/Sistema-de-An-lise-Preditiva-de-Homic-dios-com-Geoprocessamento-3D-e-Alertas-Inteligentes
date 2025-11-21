from django.shortcuts import render
from consultas.models import ComparativoPrevisoes
from collections import defaultdict
import json # 👈 Importe a biblioteca JSON

from collections import defaultdict
import json
from django.shortcuts import render
from consultas.models import ComparativoPrevisoes # Certifique-se de importar o model

def mapa(request):
    # MUDANÇA 1: Usamos 'municipio__nome' para pegar o campo 'nome' da tabela relacionada
    dados_classificacao = ComparativoPrevisoes.objects.values('municipio__nome', 'classificacao', 'ano') 
    
    dados_por_ano = defaultdict(list)

    for item in dados_classificacao:
        ano = str(item['ano']).strip()
        
        # MUDANÇA 2: A chave no dicionário 'item' agora reflete o nome do campo composto
        nome_municipio = item['municipio__nome']

        if nome_municipio and ano: 
            dados_por_ano[ano].append({
                # MUDANÇA 3: Atribuímos o nome (string) ao campo 'municipio' do JSON
                'municipio': nome_municipio, 
                'classificacao': item['classificacao']
            })
    
    # print(dados_por_ano) # Para debug
    dados_json = json.dumps(dict(dados_por_ano)) 

    contexto = {
        'dados_por_ano_json': dados_json
    }

    return render(request, 'contato.html', contexto)