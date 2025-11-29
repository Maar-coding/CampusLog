from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from web.models import Post
from web.forms import PostForm
from django.http import JsonResponse

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
    posts = Post.objects.select_related('author').all().order_by('-created_at')  # ← .all() 추가

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
        'posts': page_obj,                              # ← 기존
        'page_obj': page_obj,                           # ← 추가
        'paginator': paginator,                         # ← 추가
        'is_paginated': page_obj.has_other_pages(),     # ← 추가
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


from django.views.decorators.http import require_POST
from django.db.models import Count, Exists, OuterRef


@require_POST
@login_required
def post_like(request, postid):
    """
    POST /board/{postid}/like : 좋아요 토글
    """
    post = get_object_or_404(Post, pk=postid)

    from web.models import PostLike
    like, created = PostLike.objects.get_or_create(post=post, user=request.user)

    if not created:
        like.delete()
        return JsonResponse({'status': 'unliked', 'like_count': post.likes.count()})

    return JsonResponse({'status': 'liked', 'like_count': post.likes.count()})


@require_POST
@login_required
def comment_create(request, postid):
    """
    POST /board/{postid}/comment : 댓글 작성
    """
    post = get_object_or_404(Post, pk=postid)
    content = request.POST.get('content', '').strip()

    if not content:
        return JsonResponse({'status': 'fail', 'message': '내용을 입력하세요.'}, status=400)

    from web.models import Comment
    comment = Comment.objects.create(
        post=post,
        author=request.user,
        content=content
    )

    return JsonResponse({
        'status': 'success',
        'comment': {
            'id': comment.id,
            'author': comment.author.username,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y.%m.%d %H:%M')
        }
    })
