from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic.edit import FormView

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


def paginator_list(request, post_list):
    paginator = Paginator(post_list, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.select_related('author', 'group')
    page_obj = paginator_list(request, post_list)
    context = {
        'title': 'Последние обновления на сайте',
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author')
    page_obj = paginator_list(request, post_list)
    title = f'Записи сообщества {group.title}'
    context = {
        'title': title,
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = user.posts.select_related('group')
    page_obj = paginator_list(request, post_list)
    title = f'Профайл пользователя {username}'
    author = User.objects.get(username=username)
    following = Follow.objects.filter(author=author).exists()
    context = {
        'title': title,
        'author': user,
        'posts': post_list,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    title = f'Пост {post.text[:30]}'
    posts = Post.objects.filter(author=post.author)
    comments = Comment.objects.filter(post=post)
    context = {
        'title': title,
        'post': post,
        'posts': posts,
        'comments': comments,
        'form': CommentForm(),
    }
    return render(request, 'posts/post_detail.html', context)


class PostCreate(LoginRequiredMixin, View):

    def get(self, request):
        form = PostForm()
        return render(request, 'posts/create_post.html',
                      {'title': 'Добавить запись', 'form': form})

    def post(self, request):
        form = PostForm(request.POST, files=self.request.FILES)
        if form.is_valid():
            form_save = form.save(commit=False)
            form_save.author_id = request.user.id
            form.save()
            return redirect(reverse('posts:profile',
                                    args=[request.user.username]))
        return render(request, 'posts/create_post.html',
                      {'title': 'Добавить запись', 'form': form})


class PostEdit(FormView):
    template_name = 'posts/create_post.html'
    form_class = PostForm

    def get_post_id(self):
        return int(self.request.get_full_path().split('/')[2])

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_form(self, form_class=None):
        post_id = self.get_post_id()
        post = get_object_or_404(Post, pk=post_id)
        return PostForm(self.request.POST or None,
                        files=self.request.FILES or None,
                        instance=post)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        context_data.update({'title': 'Редактировать запись',
                             'is_edit': True})
        return context_data

    def get_success_url(self):
        post_id = self.get_post_id()
        return reverse('posts:post_detail', kwargs={'post_id': post_id})

    def get(self, request, *args, **kwargs):
        post_id = self.get_post_id()
        post = get_object_or_404(Post, pk=post_id)
        if post.author != request.user:
            return redirect(reverse('posts:post_detail',
                                    args=[post_id]))
        return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        post_id = self.get_post_id()
        post = get_object_or_404(Post, pk=post_id)
        if post.author != request.user:
            return redirect(reverse('posts:post_detail',
                                    args=[post_id]))
        return super().post(self, request, *args, **kwargs)


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator_list(request, post_list)
    context = {'page_obj': page_obj,
               'title': 'title'}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
