from django import forms

CONTEST_CHOICES = (
    ('fanduel','FANDUEL'),
    ('draftkings', 'DRAFTKINGS'),
    ('yahoo','YAHOO'),
)

class DocumentForm(forms.Form):
    contest = forms.CharField(max_length= 10, label="Select the contest",
    widget=forms.Select(choices=CONTEST_CHOICES)) 
    docfile = forms.FileField(
        label='Upload the csv file'
    )
    