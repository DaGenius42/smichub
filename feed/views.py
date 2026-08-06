from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Post, News, House
from .forms import PostForm, CommentsForm
from django.core.exceptions import PermissionDenied 
from django.views.decorators.http import require_POST
from django.db.models import Q

@login_required
def home(request):
    query = request.GET.get('q' , '').strip()
    selected_category = request.GET.get('category', '').strip()
    posts = Post.objects.select_related("author").prefetch_related("comments__author")
    news = News.objects.all()
    house = House.objects.all()
    if query:
        posts = posts.filter(
            Q(title__icontains=query) | Q(body__icontains=query) | Q(author__username__icontains=query)
        )
        news = news.filter(
            Q(title__icontains=query) | Q(body__icontains=query)
        )

    if selected_category:
        posts = posts.filter(category=selected_category)
        news = news.filter(category=selected_category)
    
    context = {
        'posts': posts,
        'query': query,
        'selected_category': selected_category,
        'categories': Post.CATEGORY_CHOICES + News.CATEGORY_CHOICES,
        'news': news,
        'houses': house,
    }
    return render(request, 'feed/home.html', context)

def about(request):
    return render(request, 'feed/about.html')

def user_post(request, post_id):
    post = get_object_or_404(Post.objects.select_related("author").prefetch_related("comments__author"), id=post_id)

    context = {
        'post': post,
        'comments_form': CommentsForm(),
    }
    return render(request, 'feed/user_post.html', context)

def news_post(request, news_id):
    news = get_object_or_404(News.objects.all(), id=news_id)
    context = {
        'news': news,
    }
    return render(request, 'feed/news_post.html', context)

@login_required
def create_post(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('feed:home')
    else:
        form = PostForm()
    return render(request, 'feed/create_post.html', {'form': form})

@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        raise PermissionDenied("You do not have permission to delete this post.")
    post.delete()
    return redirect('feed:home')

@login_required
@require_POST
def create_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentsForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('feed:user_post', post_id=post.id)

@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('feed:user_post', post_id=post.id)

@login_required
@require_POST
def like_news(request, news_id):
    news = get_object_or_404(News, id=news_id)
    if request.user in news.likes.all():
        news.likes.remove(request.user)
    else:
        news.likes.add(request.user)
    return redirect('feed:news_post', news_id=news.id)