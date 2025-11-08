from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    nome = forms.CharField(
        label='Nome completo *',
        help_text='* Campos obrigatórios',
        required=True
    )
    instituicao = forms.CharField(
        label='Instituição a que pertence *',
        help_text='Registre a instituição, ou universidade, ou empresa',
        required=True
    )
    email = forms.EmailField(
        label='Email *',
        help_text='Use um email válido. Será usado para acessar o sistema e recuperar senha!',
        required=True
    )
    celular = forms.CharField(
        label='Número celular com DDD *',
        help_text='Use DDD, por exemplo 55987619832',
        required=True
    )
    cpf = forms.CharField(label='CPF *', required=True)
    password = forms.CharField(
        label='Senha *',
        widget=forms.PasswordInput,
        required=True
    )

    class Meta:
        model = Usuario
        fields = ['nome', 'instituicao', 'email', 'celular', 'cpf', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        print(">>> __init__ do UsuarioForm executado <<<")
        print("Helper antes:", hasattr(self, 'helper'))
        self.helper = FormHelper()
        print("Helper depois:", hasattr(self, 'helper'))
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            Row(
                Column('nome', css_class='col-md-6'),
                Column('email', css_class='col-md-6'),
            ),
            Row(
                Column('instituicao', css_class='col-md-6'),
                Column('celular', css_class='col-md-6'),
            ),
            Row(
                Column('cpf', css_class='col-md-6'),
                Column('password', css_class='col-md-6'),
            ),
            Submit('submit', 'Cadastrar', css_class='btn btn-laranja mt-3')
        )
