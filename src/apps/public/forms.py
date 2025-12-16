from django import forms

from apps.accounting.models import Company

class CompanySetupForm(forms.ModelForm):
    company_name = forms.CharField(max_length=256)
    company_scale = forms.CharField(max_length=20)

    name = forms.CharField(max_length=256, required=False)
    scale = forms.ChoiceField(choices=Company.SCALE_TYPES, required=False)

    class Meta:
        model = Company
        fields = ('name', 'scale')

    def clean(self):
        cleaned_data = super().clean()
        # set field for model
        cleaned_data['name'] = cleaned_data['company_name']
        cleaned_data['scale'] = cleaned_data['company_scale']
        return cleaned_data

class CompanyUpdateForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'

