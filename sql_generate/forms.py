from django import forms

class QueryForm(forms.Form):
    table_name = forms.CharField(label='Table Name', max_length=100)
    column_name = forms.CharField(label='Column Name', max_length=100)
    values = forms.CharField(label='Values', widget=forms.Textarea)

class UploadFileForm(forms.Form):
    file = forms.FileField(required= True)
    
class CoordinatesForm(forms.Form):
    pass