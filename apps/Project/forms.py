from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['prj_name', 'prj_description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['prj_name'].widget.attrs.update({
            'minlength': 10,
            'maxlength': 50,
            'required': True,
        })
        self.fields['prj_description'].widget.attrs.update({
            'placeholder': 'Dale una descripción a tu proyecto',
            'style': 'height: 100px;',
            'required': False,
        })
