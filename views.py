import random
from django.db.models import F, Sum, Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpResponseBadRequest
from .models import Quote, Vote
from .forms import QuoteForm, SourceForm

def weighted_random_quote():
    rows = list(Quote.objects.values_list('id','weight'))
    if not rows:
        return None
    total = sum(w for _, w in rows)
    r = random.randint(1, total)
    upto = 0
    for qid, w in rows:
        upto += w
        if upto >= r:
            return Quote.objects.get(pk=qid)

def ensure_session(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key

def index(request):
    quote = weighted_random_quote()
    if quote:
        Quote.objects.filter(pk=quote.pk).update(views=F('views')+1)
        quote.refresh_from_db(fields=['views','likes','dislikes'])
    return render(request, 'quotes/index.html', {'quote': quote})

def submit_quote(request):
    if request.method == 'POST':
        q_form = QuoteForm(request.POST)
        s_form = SourceForm(request.POST, prefix='src')
        if 'create_source' in request.POST and s_form.is_valid():
            source = s_form.save()
            messages.success(request, f"Источник '{source.name}' создан — теперь добавьте цитату.")
            q_form = QuoteForm(initial={'source': source.id})
        elif q_form.is_valid():
            try:
                quote = q_form.save()
                messages.success(request, 'Цитата добавлена!')
                return redirect('quotes:index')
            except Exception as e:
                messages.error(request, f'Ошибка: {e}')
    else:
        q_form = QuoteForm()
        s_form = SourceForm(prefix='src')
    return render(request, 'quotes/submit.html', {'q_form': q_form, 's_form': s_form})

@require_POST
def vote(request, pk, action: str):
    quote = get_object_or_404(Quote, pk=pk)
    session_key = ensure_session(request)
    value = 1 if action == 'like' else -1 if action == 'dislike' else None
    if value is None:
        return HttpResponseBadRequest('Некорректное действие')
    vote, created = Vote.objects.get_or_create(quote=quote, session_key=session_key, defaults={'value': value})
    if not created and vote.value != value:
        vote.value = value
        vote.save(update_fields=['value'])
    agg = quote.votes.aggregate(
        total_likes=Count('id', filter=Q(value=1)),
        total_dislikes=Count('id', filter=Q(value=-1)),
    )
    Quote.objects.filter(pk=quote.pk).update(
        likes=agg.get('total_likes') or 0,
        dislikes=agg.get('total_dislikes') or 0,
    )
    return redirect('quotes:index')

def popular(request):
    qs = Quote.objects.all().order_by('-likes', '-views', '-created_at')
    medium = request.GET.get('medium')
    if medium:
        qs = qs.filter(source__medium=medium)
    qs = qs[:10]   # срез только после всех фильтров
    return render(request, 'quotes/popular.html', {'quotes': qs, 'medium': medium})
