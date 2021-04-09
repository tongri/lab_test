from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404

from .models import Board, Topic, Post
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from .forms import NewTopicForm, PostForm, BoardForm
from django.contrib.auth.decorators import login_required

from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.utils import timezone
from django.views.generic import UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.http import JsonResponse
from django.template.loader import render_to_string
from pdb import set_trace
from django.core.paginator import Paginator
from django.contrib import messages

from django.db.models.signals import post_save
from django.dispatch import receiver
from education.settings import AUTH_USER_MODEL
# Create your views here.


class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 1

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset

@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)

    if request.method == "POST":
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()
            post = Post.objects.create(message=form.cleaned_data.get('message'),
                topic = topic, created_by=request.user)
            return redirect('topic_posts', pk=pk, topic_pk=topic.pk)

    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts.html'
    paginate_by = 2

    def get_context_data(self, **kwargs):
        self.topic.views += 1
        self.topic.save()
        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            return redirect('topic_posts', pk=pk, topic_pk=topic_pk)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ('message', )
    template_name = "edit_post.html"
    pk_url_kwarg = "post_pk"
    context_object_name = 'post'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)


class BoardListView(ListView):
    model = Board
    context_object_name = "boards"
    template_name = "home.html"
    paginate_by = 2

    def get_context_data(self, **kwargs):
        page = self.request.GET.get('page', 1)
        return super().get_context_data(page=page, **kwargs)


def save_board_form(request, form, template_name, page, message):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            messages.success(request, message)
            p = Paginator(Board.objects.all(), BoardListView.paginate_by)
        
            boards = p.page(page)
            boards = boards.object_list
            infos = messages.get_messages(request)
            data['html_book_list'] = render_to_string('partial_board_list.html', {
                'boards': boards,
                'page': page,
                'request': request,
                'messages': infos
            })
        else:
            data['form_is_valid'] = False
    context = {'form': form, 'request': request, 'page': page}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def board_create(request, page=1):
    if request.method == 'POST':
        form = BoardForm(request.POST)
    else:
        form = BoardForm()
    return save_board_form(request, form, 'partial_board_create.html', page,
        message='Board was created successfully')

def board_update(request, pk, page=1):
    board = get_object_or_404(Board, pk=pk)
    
    if request.method == "POST":
        form = BoardForm(request.POST, instance = board)
    else:
        form = BoardForm(instance=board)
    return save_board_form(request, form, 'partial_board_update.html', page,
        message='Board was updated successfully')

def board_delete(request, pk, page=1):
    board = get_object_or_404(Board, pk=pk)
    page = int(page)
    data = dict()
    if request.method == 'POST':
        data['form_is_valid'] = True
        
        p = Paginator(Board.objects.all(), BoardListView.paginate_by)
        
        boards = p.page(page)
        boards = boards.object_list
        
        board.delete()
        messages.success(request, 'Board was deleted successfully!')
        data['html_book_list'] = render_to_string('partial_board_list.html', {
            'boards': boards,
            'request': request,
            'page': page
        })
    else:
        context = {'board': board, 'page': page}
        data['html_form'] = render_to_string('partial_board_delete.html',
            context,
            request=request,
        )
    return JsonResponse(data)
