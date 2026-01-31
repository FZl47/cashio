import os
from django import forms

from . import models


class ResourceFolderCreateForm(forms.ModelForm):
    class Meta:
        model = models.FolderResource
        exclude = ('type',)


class ResourceFileCreateForm(forms.ModelForm):
    class Meta:
        model = models.FileResource
        exclude = ('type',)


class FileRawUploadForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['extension'].required = False
        self.fields['size'].required = False

    class Meta:
        model = models.FileRaw
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        file = self.files.get('file')
        if file:
            _, ext = os.path.splitext(file.name)
            extension = ext.lstrip('.')
            cleaned_data['extension'] = extension
            cleaned_data['size'] = round((file.size / 1024), 2)  # Convert bytes to kilobytes
        return cleaned_data
