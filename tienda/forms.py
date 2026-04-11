import re
from django import forms
from .models import Usuarios


class RegistroForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        min_length=2,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Tu nombre',
            'id': 'registro-nombre',
        }),
        error_messages={
            'min_length': 'El nombre debe tener al menos 2 caracteres.',
            'required': 'El nombre es obligatorio.',
        }
    )
    apellido = forms.CharField(
        max_length=100,
        min_length=2,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Tu apellido',
            'id': 'registro-apellido',
        }),
        error_messages={
            'min_length': 'El apellido debe tener al menos 2 caracteres.',
            'required': 'El apellido es obligatorio.',
        }
    )
    usuario = forms.CharField(
        max_length=100,
        min_length=4,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nombre de usuario',
            'id': 'registro-usuario',
        }),
        error_messages={
            'min_length': 'El nombre de usuario debe tener al menos 4 caracteres.',
            'required': 'El nombre de usuario es obligatorio.',
        }
    )
    contrasenia = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Contraseña',
            'id': 'registro-password',
        }),
        error_messages={
            'min_length': 'La contraseña debe tener al menos 8 caracteres.',
            'required': 'La contraseña es obligatoria.',
        }
    )
    confirmar_contrasenia = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirmar contraseña',
            'id': 'registro-confirm-password',
        }),
        error_messages={
            'required': 'Debes confirmar la contraseña.',
        }
    )

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$', nombre):
            raise forms.ValidationError(
                'El nombre solo puede contener letras y espacios.'
            )
        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido', '').strip()
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$', apellido):
            raise forms.ValidationError(
                'El apellido solo puede contener letras y espacios.'
            )
        return apellido

    def clean_usuario(self):
        usuario = self.cleaned_data.get('usuario', '').strip()
        if not re.match(r'^[a-zA-Z0-9_-]+$', usuario):
            raise forms.ValidationError(
                'El nombre de usuario solo puede contener letras, números, '
                'guiones (-) y guiones bajos (_).'
            )
        if Usuarios.objects.filter(usuario=usuario).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return usuario

    def clean_contrasenia(self):
        contrasenia = self.cleaned_data.get('contrasenia', '')
        if not re.search(r'[A-Z]', contrasenia):
            raise forms.ValidationError(
                'La contraseña debe contener al menos una letra mayúscula.'
            )
        if not re.search(r'[a-z]', contrasenia):
            raise forms.ValidationError(
                'La contraseña debe contener al menos una letra minúscula.'
            )
        if not re.search(r'[0-9]', contrasenia):
            raise forms.ValidationError(
                'La contraseña debe contener al menos un número.'
            )
        return contrasenia

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('contrasenia')
        confirm = cleaned_data.get('confirmar_contrasenia')
        if password and confirm and password != confirm:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data


class LoginForm(forms.Form):
    usuario = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Nombre de usuario',
            'id': 'login-usuario',
        }),
        error_messages={
            'required': 'El nombre de usuario es obligatorio.',
        }
    )
    contrasenia = forms.CharField(
        min_length=1,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Contraseña',
            'id': 'login-password',
        }),
        error_messages={
            'required': 'La contraseña es obligatoria.',
        }
    )

    def clean_usuario(self):
        """Limpiar espacios en blanco al inicio y final del usuario."""
        return self.cleaned_data.get('usuario', '').strip()

