from django import forms
from django_countries.fields import CountryField


class PaymentForm(forms.Form):
    Name = forms.CharField(max_length=16)
    Country = CountryField().formfield()
    Amount = forms.DecimalField(max_digits=6, decimal_places=2)

    def clean(self):
        cleaned_data = super(PaymentForm, self).clean()
        Name = cleaned_data.get('Name')
        Country = cleaned_data.get('Country')
        Amount = cleaned_data.get('Amount')
        if not Name and not Country and not Amount:
            raise forms.ValidationError('You have to Enter something!') 


class ColorfulPaymentForm(forms.Form):
    name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'style': 'border-color: blue;',
                'placeholder': 'Write your name here'
            }
        )
    )
    email = forms.EmailField(
        max_length=254,
        widget=forms.TextInput(attrs={'style': 'border-color: green;'})
    )
    message = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(attrs={'style': 'border-color: orange;'}),
        help_text='Write here your message!'
    )
