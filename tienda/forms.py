from django import forms
from .models import Usuarios


class RegistroForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Tu nombre',
            'id': 'registro-nombre',
        })
    )
    apellido = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Tu apellido',
            'id': 'registro-apellido',
        })
    )
    usuario = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nombre de usuario',
            'id': 'registro-usuario',
        })
    )
    contrasenia = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Contraseña',
            'id': 'registro-password',
        })
    )
    confirmar_contrasenia = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirmar contraseña',
            'id': 'registro-confirm-password',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('contrasenia')
        confirm = cleaned_data.get('confirmar_contrasenia')
        if password and confirm and password != confirm:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data

    def clean_usuario(self):
        usuario = self.cleaned_data.get('usuario')
        if Usuarios.objects.filter(usuario=usuario).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return usuario


class LoginForm(forms.Form):
    usuario = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nombre de usuario',
            'id': 'login-usuario',
        })
    )
    contrasenia = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Contraseña',
            'id': 'login-password',
        })
    )
