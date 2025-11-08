# views.py
from django.shortcuts import render, redirect
from .forms import UsuarioForm

def cadastro(request):
    form = UsuarioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('cadastro')  # ou onde fizer sentido
    return render(request, 'contato.html', {'form': form})
