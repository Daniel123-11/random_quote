from django.db import models
from django.core.exceptions import ValidationError

class Source(models.Model):
    MEDIUM_CHOICES = [
        ('movie', 'Фильм'),
        ('book', 'Книга'),
        ('series', 'Сериал'),
        ('other', 'Другое'),
    ]
    name = models.CharField(max_length=200, unique=True)
    medium = models.CharField(max_length=20, choices=MEDIUM_CHOICES, default='other')
    def __str__(self): return self.name

class Quote(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='quotes')
    text = models.TextField(unique=True)
    weight = models.PositiveIntegerField(default=1)
    views = models.PositiveIntegerField(default=0)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
    def clean(self):
        if self.source_id:
            existing = Quote.objects.filter(source_id=self.source_id)
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            if existing.count() >= 3:
                raise ValidationError('У одного источника не может быть больше трёх цитат.')
        if self.weight < 1:
            raise ValidationError('Вес должен быть положительным.')
    def __str__(self): return self.text[:60]

class Vote(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='votes')
    session_key = models.CharField(max_length=40, db_index=True)
    value = models.SmallIntegerField(choices=[(-1, 'Дизлайк'), (1, 'Лайк')])
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('quote', 'session_key')
