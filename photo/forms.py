from django import forms
from .models import Document

class DocumentForm(forms.ModelForm):
    class Meta():        
        model = Document
        fields = ('document', )

class DocumentNameForm(forms.ModelForm):
    class Meta():
        model = Document
        fields = ('filename', 'user_id', 'email', 'document', )