from django import forms
from .models import Quote, Source

class SourceForm(forms.ModelForm):
    class Meta:
        model = Source
        fields = ['name', 'medium']

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['source', 'text', 'weight']
        widgets = {'text': forms.Textarea(attrs={'rows':4})}

    def clean(self):
        cleaned = super().clean()
        source = cleaned.get('source')
        if source:
            cnt = Quote.objects.filter(source=source)
            if self.instance.pk:
                cnt = cnt.exclude(pk=self.instance.pk)
            if cnt.count() >= 3:
                raise forms.ValidationError('Для этого источника уже есть 3 цитаты.')
        return cleaned
