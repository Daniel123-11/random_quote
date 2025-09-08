from django.contrib import admin
from .models import Source, Quote, Vote

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'medium')
    search_fields = ('name',)

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('short_text', 'source', 'weight', 'views', 'likes', 'dislikes', 'created_at')
    list_filter = ('source__medium',)
    search_fields = ('text','source__name')
    def short_text(self, obj):
        return (obj.text[:60] + '…') if len(obj.text) > 60 else obj.text

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('quote','session_key','value','created_at')
    search_fields = ('session_key','quote__text')
