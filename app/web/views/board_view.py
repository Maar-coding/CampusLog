from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# ==================================================================
# 2. 게시판 뷰 (HTML 렌더링)
# ==================================================================
def board(request):
    return render(request, 'web/board.html')



def board_list(request, category):
    # (신규) GET, POST /board/{category}

    if request.method == 'POST':
        # (신규) POST : 작성된 게시글을 저장 (로그인 필요)
        pass  # ⬅️ 여기에 게시글 "저장" 로직 구현

    # GET: 게시판 목록 화면
    # posts = Post.objects.filter(category=category)
    # context = {'category': category, 'posts': posts}
    # return render(request, 'web/board_list.html', context)
    pass  # ⬅️ 여기에 게시글 "목록" 로직 구현


def post_detail(request, category, postid):
    # (신규) GET /board/{category}/{postid} : 게시글 상세 화면
    # post = get_object_or_404(Post, pk=postid, category=category)
    # context = {'post': post}
    # return render(request, 'web/post_detail.html', context)
    pass  # ⬅️ 여기에 게시글 "상세" 로직 구현


@login_required  # 명세서: "로그인 필요"
def post_write_form(request, category):
    # (신규) GET /board/{category}/write : 게시글 작성 폼
    # context = {'category': category}
    # return render(request, 'web/post_write_form.html', context)
    pass  # ⬅️ 여기에 게시글 "작성 폼" 로직 구현