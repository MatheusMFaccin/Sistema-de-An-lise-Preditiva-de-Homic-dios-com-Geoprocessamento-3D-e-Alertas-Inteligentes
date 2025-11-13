from django.shortcuts import render
from consultas.models import ComparativoPrevisoes
from collections import defaultdict
import json # 👈 Importe a biblioteca JSON

def cadastro(request):
 
    dados_classificacao = ComparativoPrevisoes.objects.values('municipio', 'classificacao', 'ano') 

    
    dados_por_ano = defaultdict(list)

    for item in dados_classificacao:
        ano = str(item['ano']).strip()
        
        if item['municipio'] and ano: 
            dados_por_ano[ano].append({
                'municipio': item['municipio'],
                'classificacao': item['classificacao']
            })
    
    print(dados_por_ano)
    dados_json = json.dumps(dict(dados_por_ano)) 


    contexto = {
        'dados_por_ano_json': dados_json
    }

    return render(request, 'contato.html', contexto)