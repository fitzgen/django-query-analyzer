from query_analyzer.shortcuts import list_models

from django import forms
#from django.contrib.admin.helpers import AdminForm
from django.conf import settings

class PythonForm(forms.Form):
    model = forms.ChoiceField(choices=list_models(), label="Choose a model")
    python = forms.CharField(label="Enter some python", required=False, 
        widget=forms.Textarea(attrs={"rows":"2"}))
    
def FieldsForm(model):
    form = type("FieldsForm", (forms.ModelForm,), dict(Meta=type("Meta", (object,), dict(model=model))))
    return form()
    
