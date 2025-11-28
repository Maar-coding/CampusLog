from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from web.models import Post
from web.forms import PostForm
from django.http import JsonResponse

def board(request):
    """메인 게시판 페이지"""
    return render(request, 'web/board_panel.html')


def board_list(request):
    """
    GET /board/list : 게시판 목록 조회
    POST /board/list : 게시글 작성 (로그인 필요)
    """
    if request.method == 'POST':
        # 로그인 체크
        if not request.user.is_authenticated:
            messages.error(request, '로그인이 필요합니다.')
            return redirect('login')

        # 게시글 작성 처리
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, '게시글이 작성되었습니다.')
            return redirect('post_detail', postid=post.id)
        else:
            messages.error(request, '게시글 작성에 실패했습니다.')

    # GET 요청: 게시글 목록 조회
    posts = Post.objects.select_related('author')

    # 검색 기능
    query = request.GET.get('q')
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )

    # 페이지네이션 (한 페이지에 15개)
    paginator = Paginator(posts, 15)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)

    context = {
        'posts': page_obj,
        'query': query,
    }

    return render(request, 'web/board_panel.html', context)


def post_detail(request, postid):
    """
    GET /board/{postid} : 게시글 상세 조회
    """
    post = get_object_or_404(
        Post.objects.select_related('author'),
        pk=postid
    )

    context = {
        'post': post,
    }

    return render(request, 'web/board_detail_panel.html', context)


@login_required
def post_write_form(request):
    """
    GET /board/write : 게시글 작성 폼
    """
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            # JSON으로 성공 응답 보냄
            return JsonResponse({
                'status': 'success',
                'post_id': post.id,
                'message': '게시글이 등록되었습니다.'
            })
        else:
            return JsonResponse({'status': 'fail', 'errors': form.errors}, status=400)

    else:
        form = PostForm()

    return render(request, 'web/board_upload.html', {'form': form})