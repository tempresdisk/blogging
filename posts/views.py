from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


def index(request):
    post_list = Post.objects.select_related('group', 'author').prefetch_related('comments')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
         request,
         'index.html',
         {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author').prefetch_related('comments').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
         request,
         "group.html",
         {"group": group, "page": page, "paginator": paginator}
    )


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('index')
    return render(request, 'new_post.html', {'form': form, 'is_edit': False})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group').prefetch_related('comments').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = request.user.follower.filter(author=author).exists()
    context = {"page": page, "author": author,
               "paginator": paginator, 'following': following}
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post.objects.select_related('author'), id=post_id, author__username=username)
    post_list = post.author.posts.all()
    post_count = post_list.count()
    comments = Comment.objects.filter(post=post)
    form = CommentForm(request.POST or None)
    following = False
    if request.user.is_authenticated:
        following = request.user.follower.filter(author=post.author).exists()
    context = {'post': post, 'post_count': post_count, 'author': post.author,
               'comments': comments, 'form': form, 'following': following}
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    if username != request.user.username:
        return redirect('post', username, post_id)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('post', username, post_id)
    return render(request,
                  'new_post.html',
                  {'form': form, 'is_edit': True, 'post': post})


def page_not_found(request, exception=None):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('post', username, post_id)
    return redirect('post', username, post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.select_related('group').filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
         request,
         'follow.html',
         {'page': page, 'paginator': paginator, }
    )


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if author != user and not user.follower.filter(author=author).exists():
        Follow.objects.create(user=user, author=author)
        return redirect(request.META.get('HTTP_REFERER',
                        reverse('profile', args=[username])))
    return redirect(request.META.get('HTTP_REFERER',
                    reverse('profile', args=[username])))


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect(request.META.get('HTTP_REFERER',
                    reverse('profile', args=[username])))
