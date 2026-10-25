from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Post, News, House, Comments, CustomUser, Vote, Price, Notification
from .forms import PostForm, CommentsForm, ProfileForm, VoteForm
from django.core.exceptions import PermissionDenied 
from django.views.decorators.http import require_POST
from django.db.models import Q
from .forms import CustomUserForm


def create_notification(recipient, actor, notification_type, post=None, message=""):
    """Create a notification unless the recipient is the actor themselves."""
    if recipient is None or recipient == actor:
        return
    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        notification_type=notification_type,
        post=post,
        message=message,
    )

@login_required
def home(request):
    query = request.GET.get('q' , '').strip()
    selected_category = request.GET.get('category', '').strip()
    posts = Post.objects.select_related("author").prefetch_related("comments__author").filter(verified=True).order_by('-created_at')
    if query:
        posts = posts.filter(
            Q(title__icontains=query) | Q(body__icontains=query) | Q(author__username__icontains=query)
        )

    if selected_category:
        posts = posts.filter(category=selected_category)

    news = News.objects.all().order_by('-created_at')
    
    context = {
        'posts': posts,
        'news': news,
        'query': query,
        'selected_category': selected_category,
        'categories': Post.CATEGORY_CHOICES + News.CATEGORY_CHOICES,
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
        form = PostForm(request.POST, request.FILES)#also files for pictures
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            # Let everyone else know a new post was published.
            others = CustomUser.objects.exclude(pk=request.user.pk)
            Notification.objects.bulk_create([
                Notification(
                    recipient=user,
                    actor=request.user,
                    notification_type='new_post',
                    post=post,
                    message=f"{request.user.username} shared a new post: {post.title}",
                )
                for user in others
            ])
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
        create_notification(
            post.author,
            request.user,
            'comment',
            post,
            f"{request.user.username} commented on your post: {post.title}",
        )
    return redirect('feed:user_post', post_id=post.id)

@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
        create_notification(
            post.author,
            request.user,
            'like',
            post,
            f"{request.user.username} liked your post: {post.title}",
        )
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

def signup(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('accounts:login')
    else:
        form = CustomUserForm()
    return render(request, 'registrations/signup.html', {'form': form})


@login_required
def profile(request):
    """Show the logged-in user's profile: bio, picture, and post history."""
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    context = {
        'profile_user': request.user,
        'posts': posts,
    }
    return render(request, 'feed/profile.html', context)


@login_required
def edit_profile(request):
    """Edit username, bio, and profile picture."""
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('feed:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'feed/edit_profile.html', {'form': form})

@login_required
def cc(request):
    return render(request, 'feed/cc.html')

@login_required
def stuco(request):
    news = News.objects.all().order_by('-created_at')
    context = {
        'news': news,
    }
    return render(request, 'feed/stuco.html', context)

@login_required
def cc(request):
    votes = Vote.objects.all().order_by('-created_at')
    prices = Price.objects.all()
    context = {
        'votes': votes,
        'prices': prices,
    }
    return render(request, 'feed/cc.html', context)

@login_required
def notifications(request):
    qs = Notification.objects.filter(
        recipient=request.user
    ).select_related('actor', 'post', 'news')
    # Remember which ones were unread so the page can highlight them,
    # then clear the red bubble by marking them as read.
    unread_ids = list(qs.filter(is_read=False).values_list('id', flat=True))
    if unread_ids:
        Notification.objects.filter(id__in=unread_ids).update(is_read=True)
    context = {
        'notifications': qs,
        'unread_ids': unread_ids,
    }
    return render(request, 'feed/notifications.html', context)

@login_required
def house_standings(request):
    houses = House.objects.all().order_by('-points')
    context = {
        'houses': houses,
    }
    return render(request, 'feed/house_standings.html', context)

@login_required
def create_vote(request):
    if request.method == 'POST':
        form = VoteForm(request.POST)
        if form.is_valid():
            vote = form.save(commit=False)
            vote.save()
            return redirect('feed:cc')
    else:
        form = VoteForm()
    return render(request, 'feed/create_vote.html', {'form': form})

def vote_vote(request, vote_id):
    vote = get_object_or_404(Vote, id=vote_id)
    if request.method == 'POST':
        if request.user in vote.voters.all():
            vote.voters.remove(request.user)
        else:
            vote.voters.add(request.user)
        return redirect('feed:cc')
    return redirect('feed:cc')

def like_price(request, price_id):
    price = get_object_or_404(Price, id=price_id)
    if request.user in price.thumbs.all():
        price.thumbs.remove(request.user)
    else:
        price.thumbs.add(request.user)
    return redirect('feed:cc')

def view_profile(request, username):
    user = get_object_or_404(CustomUser, username=username)
    posts = Post.objects.filter(author=user).order_by('-created_at')
    context = {
        'profile_user': user,
        'posts': posts,
    }
    return render(request, 'feed/view_profile.html', context)


@login_required
def search_users(request):
    """Return matching users as JSON for the navbar user-search dropdown."""
    q = request.GET.get('q', '').strip()
    users = CustomUser.objects.filter(username__icontains=q)[:8]
    data = [
        {
            'username': u.username,
            'bio': u.bio,
            'avatar_url': u.profile_picture.url if u.profile_picture else None,
            'initial': u.username[:1].upper(),
            'profile_url': reverse('feed:view_profile', args=[u.username]),
        }
        for u in users
    ]
    return JsonResponse({'users': data})