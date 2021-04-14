from django.contrib import messages
from django.forms import modelformset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.core.cache import cache
from django.urls import reverse
from django.views.generic.base import View

from .models import Board, Topic, Post, User, Image
from .forms import NewTopicForm, PostForm, BoardForm, PhotoForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone
from django.views.generic import UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.core.paginator import Paginator
import xlwt
import datetime

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch



class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    #paginate_by = 1

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
            Post.objects.create(message=form.cleaned_data.get('message'),
                                       topic=topic, created_by=request.user)
            photos = request.FILES.getlist('file_field')
            if photos:
                photos_form = PhotoForm(*photos)
                if photos_form.is_valid():
                    for photo_form in photos_form:
                        photo_form.topic = topic
                        photo_form.save()
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
    fields = ('message',)
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
        infos = cache.get('notifications')
        return super().get_context_data(page=page, infos=infos, **kwargs)


def add_to_cache(message):
    notification = cache.get('notifications')
    if notification:
        notification = [message] + notification[:4]
        cache.set('notifications', notification, 60 * 15)
    else:
        cache.set('notifications', [message], 60 * 15)


def photo_create(request, pk):
    data = dict()
    board = Board.objects.get(pk=pk)
    if request.method == "POST":
        photo = request.FILES.get('file')
        data = {'is_valid': True, 'name': photo.file.name, 'url': photo.file.name}
        return JsonResponse(data)


def save_board_form(request, form, template_name, page, message):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            p = Paginator(Board.objects.all(), BoardListView.paginate_by)
            boards = p.page(page)
            boards = boards.object_list
            add_to_cache(message.format(form.cleaned_data.get('name')))

            data['html_book_list'] = render_to_string('partial_board_list.html', {
                'boards': boards,
                'page': page,
                'request': request,
                'messages': (message,)
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
                           message=f'Board "{form.data}" was created successfully')


def board_update(request, pk, page=1):
    board = get_object_or_404(Board, pk=pk)

    if request.method == "POST":
        form = BoardForm(request.POST, instance=board)
    else:
        form = BoardForm(instance=board)
    return save_board_form(request, form, 'partial_board_update.html', page,
                           message=f'Board "{form.data}" was updated successfully')


def board_delete(request, pk, page=1):
    board = get_object_or_404(Board, pk=pk)
    page = int(page)
    data = dict()
    if request.method == 'POST':
        data['form_is_valid'] = True

        p = Paginator(Board.objects.all(), BoardListView.paginate_by)

        boards = p.page(page)
        boards = boards.object_list

        message = 'Board "{}" was deleted successfully!'.format(board.name)

        add_to_cache(message)
        board.delete()
        data['html_book_list'] = render_to_string('partial_board_list.html', {
            'boards': boards,
            'request': request,
            'page': page,
            'messages': (message,)
        })
    else:
        context = {'board': board, 'page': page}
        data['html_form'] = render_to_string('partial_board_delete.html',
                                             context,
                                             request=request,
                                             )
    return JsonResponse(data)


def export_topics_xls(request, pk):
    try:
        board = Board.objects.get(pk=pk)
        rows = board.topics.values_list('subject', 'last_updated', 'starter', 'views')
    except:
        messages.error(request, 'no such board')
        return HttpResponseRedirect(reverse('boards', {pk: pk}))
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="topics_{board.name}.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Topics')

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Subject', 'Last Updated', 'User', 'Views', ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    for row in rows:
        row_num += 1
        row = list(row)
        row[-2] = User.objects.get(id=row[-2]).username
        for col_num in range(len(row)):
            ws.write(row_num, col_num,
                     row[col_num].utcnow().strftime("%m/%d/%Y, %H:%M:%S")
                     if isinstance(row[col_num], datetime.datetime) else row[col_num],
                     font_style)

    wb.save(response)
    return response


def export_topics_pdf(request, pk):
    cm = 2.54

    try:
        board = Board.objects.get(pk=pk)
        rows = board.topics.values_list('subject', 'last_updated', 'starter', 'views')
    except:
        messages.error(request, 'no such board')
        return HttpResponseRedirect(reverse('boards', {pk: pk}))

    doc = SimpleDocTemplate(f"/tmp/{board.name}_topics.pdf")
    styles = getSampleStyleSheet()
    Story = [Spacer(1, 2)]
    style = styles["Normal"]
    p = Paragraph(f'{board.name.capitalize()} topics', style)
    Story.append(p)
    Story.append(Spacer(1, 0.15 * inch))
    for i in rows:
        bogustext = f'Name: {i[0]} Last_update: {i[1].utcnow().strftime("%m/%d/%Y, %H:%M:%S")} ' \
                    f'User: {User.objects.get(id=i[2])} Views: {i[3]}'
        p = Paragraph(bogustext, style)
        Story.append(p)
        Story.append(Spacer(1, 0.1 * inch))
    doc.build(Story)

    fs = FileSystemStorage("/tmp")
    with fs.open(f"{board.name}_topics.pdf") as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{board.name}_topics.pdf"'
        return response

    return response

