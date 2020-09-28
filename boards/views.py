from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView, ListView
from django.utils import timezone

from .models import Board, Post, Topic
from .forms import NewTopicForm, TopicReplyForm


def home(request):
    return render(request, 'boards/home.html', {'boards': Board.objects.all()})


class Home(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'boards/home.html'


def board_topics(request, pk):
    board = get_object_or_404(Board, pk=pk)
    return render(request, 'boards/topics.html', {'board': board})


class BoardTopicsListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'boards/topics.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated')
        return queryset


@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    user = request.user
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = user
            topic.save()
            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=user
            )
            return redirect(reverse('board_topics', kwargs={'pk': board.pk}))
    elif request.method == 'GET':
        form = NewTopicForm()
    return render(request, 'boards/new_topic.html', {'form': form, 'board': board})


def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    topic.views += 1
    topic.save()
    return render(request, 'boards/topic_posts.html', {'topic': topic})


class TopicPostsListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'boards/topic_posts.html'
    paginate_by = 2

    def get_context_data(self, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True
        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset

@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    user = request.user
    if request.method == 'GET':
        form = TopicReplyForm()
    elif request.method == 'POST':
        form = TopicReplyForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = user
            post.save()

            topic.last_updated = timezone.now()
            topic.save()

            return redirect(reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk}))

    return render(request, 'boards/reply_topic.html', {'topic': topic, 'form': form})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ('message',)
    template_name = 'boards/edit_post.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_pk'

    def test_func(self):
        post_pk = int(self.kwargs['post_pk'])
        post = get_object_or_404(Post, pk=post_pk)
        return self.request.user == post.created_by

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email')
    template_name = 'boards/my_account.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return self.request.user
