
// 로그아웃 함수
function logout() {
    console.log("로그아웃 함수");
}


// 매장 필터링 함수
function onFilterClick(tag, clickedEl) {
    // 1) 기존 식당 필터링
    loadStores(tag);

    // 2) 모든 필터 버튼을 순회하면서 블러 처리
    const filters = document.querySelectorAll('.search_panel_filter');

    filters.forEach(img => {
        if (img === clickedEl) {
            // 클릭된 버튼: 블러 제거
            img.classList.remove('blurred-filter');
        } else {
            // 나머지 2개: 블러 적용
            img.classList.add('blurred-filter');
        }
    });
}

function loadStores(tag) {
    
    // 식당이 없다면
    if (!storeData || storeData.length === 0) {
        console.warn("storeData가 아직 비었습니다. 먼저 loadRestaurantDataFromDB()를 호출하세요.");
        return;
    }

    const filtered = storeData.filter(store => store.tags.includes(tag));

    // 패널 리스트만 필터링해서 다시 렌더링
    renderStoreList(filtered);
}

// 정렬방법 드롭다운 텍스트 바꾸기
function initSortDropdown() {
    const button = document.getElementById("sort_dropdown_button");
    const menu = document.getElementById("sort_dropdown_menu");

    // 요소 못 찾으면 바로 종료 (다른 패널에서 불렸을 때 대비)
    if (!button || !menu) {
        console.warn("정렬 드롭다운 요소를 찾지 못했습니다.");
        return;
    }

    // menu == NULL이면 오류, 오류방지 위치 (위 코드에서 잡아줌)
    const items = menu.querySelectorAll(".dropdown_list");

    // 버튼 클릭 → 메뉴 열기/닫기
    button.addEventListener("click", (e) => {
        e.stopPropagation();
        menu.classList.toggle("open");
    });

    // li 클릭 이벤트 등록
    items.forEach(item => {
        item.addEventListener("click", () => {

            // 1️⃣ 버튼 텍스트 변경
            button.childNodes[0].textContent = item.textContent;

            // 2️⃣ 드롭다운 닫기
            menu.classList.remove("open");

            // 3️⃣ 선택된 항목에 따라 함수 실행
            handleSort(item.textContent);
        });
    });

    // 바깥 클릭하면 닫기
    document.addEventListener("click", (e) => {
        if (!e.target.closest(".dropdown")) {
            menu.classList.remove("open");
        }
    });
}

// 회원가입 폼 AJAX 제출 + 성공 팝업 → 로그인 패널 이동
// 회원가입 폼 AJAX 제출 + 성공 팝업 → 로그인 패널 이동
function handleRegisterSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    fetch(form.action, {
        method: form.method || "POST",
        body: formData,
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        },
    })
            .then(async (res) => {
                const html = await res.text();       // 응답 본문 텍스트로 읽기
                const panel = document.getElementById("panel");

                // 1️⃣ 중복 아이디 케이스 탐지 (응답 내용으로 판단)
                //   → Network 탭 Response 안에 실제 문구에 맞춰서 수정해도 됨
                if (
                        html.includes("중복된 아이디") ||
                        html.includes("이미 존재하는 아이디")
                ) {
                    openPopup("이미 사용 중인 아이디입니다.\n다른 아이디를 사용해 주세요.");
                    return;
                }

                // 2️⃣ 템플릿에서 form.errors / error_message 로 렌더된 경우
                if (html.includes('id="registerError"')) {
                    panel.innerHTML = html;   // 에러 포함된 register 패널 다시 렌더링
                    return;
                }

                // 3️⃣ 여기까지 왔는데 상태 코드가 200이 아니면 → 진짜 서버 오류 취급
                if (!res.ok) {
                    console.error("회원가입 서버 오류:", res.status);
                    openPopup(
                            "회원가입 중 서버 오류가 발생했습니다.\n잠시 후 다시 시도해 주세요."
                    );
                    return;
                }

                // 4️⃣ 모든 에러 조건에 안 걸렸으면 → 회원가입 성공으로 간주
                openPopup("회원가입에 성공하였습니다!", () => {
                    // 확인 누르면 로그인 패널로 이동
                    changePanel("login");
                });
            })
            .catch((err) => {
                console.error("회원가입 요청 실패", err);
                openPopup(
                        "네트워크 오류가 발생했습니다.\n잠시 후 다시 시도해 주세요."
                );
            });

    return false;
}


// 로그인 폼 AJAX 제출 + 실패 시 패널 안에서만 갱신 + 성공 시 팝업 후 search 패널로 이동
function handleLoginSubmit(event) {
    event.preventDefault();  // 기본 폼 전송 막기

    const form = event.target;
    const formData = new FormData(form);

    fetch(form.action, {
        method: form.method || "POST",
        body: formData,
        headers: {
            "X-Requested-With": "XMLHttpRequest"
        },
        redirect: "follow"   // 기본값이지만 명시
    })
            .then(async (res) => {
                const html = await res.text();      // 응답 전체를 문자열로
                const panel = document.getElementById("panel");

                // 🔹 1) 진짜 서버 오류 (500 등)
                if (!res.ok && !res.redirected) {
                    console.error("로그인 서버 오류:", res.status);
                    openPopup("로그인 중 서버 오류가 발생했습니다.\n잠시 후 다시 시도해 주세요.");
                    return;
                }

                // 🔹 2) 로그인 실패 케이스
                //    - Django 기본 LoginView는 실패 시 redirect 없이 로그인 템플릿을 다시 렌더링
                //    - 그 템플릿 안에 우리가 만든 id="loginError"가 들어 있음
                if (!res.redirected && html.includes('id="loginError"')) {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, "text/html");
                    const loginPanel = doc.querySelector(".panel_case.login_panel");

                    if (loginPanel) {
                        // 패널 영역만 다시 교체
                        panel.innerHTML = loginPanel.outerHTML;
                    } else {
                        // 혹시 구조가 달라졌으면 그대로 넣어서라도 에러 메시지 보이게
                        panel.innerHTML = html;
                    }
                    return;
                }

                // 🔹 3) 여기까지 왔으면 = 대부분 "로그인 성공" (리다이렉트가 있었던 경우)
                openPopup("로그인에 성공하였습니다!", () => {
                    // 팝업의 확인 버튼을 누르면, 패널 내용만 search 패널로 교체
                    changePanel("search");
                });
            })
            .catch((err) => {
                console.error("로그인 요청 실패", err);
                openPopup("네트워크 오류가 발생했습니다.\n잠시 후 다시 시도해 주세요.");
            });

    return false;   // onsubmit="return handleLoginSubmit(event)" 에서 기본 제출 막기
}


// 정렬방법 드롭다운 선택시 함수 실행
// 정렬방법 선택시 API 호출 기준 변경
function handleSort(type) {
    if (type === "가나다순")      loadRestaurants("name");
    else if (type === "별점순")   loadRestaurants("rating");
    else if (type === "거리순")   loadRestaurants("distance");
    else if (type === "리뷰개수순") loadRestaurants("review");
}

// ✅ storeData 기준으로 정렬해서 화면에 뿌리는 함수
function loadRestaurants(sortKey) {
    // 기존 데이터 복사
    let sorted = [...storeData];

    if (sortKey === "name") {
        sorted.sort((a, b) => a.name.localeCompare(b.name)); // 가나다순
    }

    // 별점, 거리, 리뷰개수는 나중에 데이터 생기면 추가
    // else if (sortKey === "rating") { ... }
    // else if (sortKey === "distance") { ... }
    // else if (sortKey === "review") { ... }

    renderStoreList(sorted);
}


// 백엔드 데이터 연동으로 변경 필요

/* ---------------------------
1) 식당 데이터 리스트
---------------------------- */
let storeData = [];

// 2. 백엔드에서 데이터 가져오는 함수 생성
function loadRestaurantDataFromDB() {
    // fetch('/api/restaurants') // 우리가 만든 API 호출
    //     .then(res => res.json())
    //     .then(data => {
    //         console.log("식당 데이터 로드 완료:", data);

    //         // (1) 전역 변수 storeData 업데이트
    //         storeData = data;

    //         // (2) 지도에 마커 찍기
    //         storeData.forEach(store => {
    //             createMarker(store.lat, store.lng, store.tags, store.id);
    //         });

    //             // (3) 패널에 리스트 렌더링 (초기화)
    //         renderStoreList(storeData);
    //     })
    //     .catch(err => console.error("식당 데이터 로드 실패:", err));
    const storeData = [
      {
        id: 1,
        name: "맛있는 김밥천국",
        img: "https://via.placeholder.com/200x150?text=Gimbap",
        openTime: "09:00",
        closeTime: "22:00",
      },
      {
        id: 2,
        name: "스시 월드",
        img: "https://via.placeholder.com/200x150?text=Sushi",
        openTime: "11:30",
        closeTime: "23:00",
      },
      {
        id: 3,
        name: "카페 달콤",
        img: "https://via.placeholder.com/200x150?text=Cafe",
        openTime: "08:00",
        closeTime: "20:00",
      }
    ];
     renderStoreList(storeData);
}


/* ---------------------------
2) 리스트 렌더 함수
---------------------------- */
function renderStoreList(list) {
    const container = document.getElementById("store_list");
    const template = document.getElementById("store_card_template");

    container.innerHTML = "";

    if (!list || list.length === 0) {
        container.innerHTML = `<p class="no_result">검색 결과가 없습니다.</p>`;
        return;
    }

    list.forEach(store => {
        const clone = template.content.cloneNode(true);

        // ⭐ store_card div에 id 주입
        const card = clone.querySelector(".store_card");
        card.dataset.id = store.id;

        clone.querySelector(".store_img").src = store.image;
        clone.querySelector(".store_name").textContent = store.name;
        clone.querySelector(".store_time").textContent = store.time;

        // ⭐ "식당 세부 페이지" 클릭 이벤트 연결
        const nameBtn = clone.querySelector(".store_name");
        nameBtn.addEventListener("click", function () {
            const id = card.dataset.id;       // ⭐ 카드에서 id 가져오기
            openReviewPanel("restaurant", id);
        });

        // ⭐ "후기 보기" 클릭 이벤트 연결
        const reviewBtn = clone.querySelector(".store_review");
        reviewBtn.addEventListener("click", function () {
            const id = card.dataset.id;       // ⭐ 카드에서 id 가져오기
            openReviewPanel("restaurant_reviews", id);
        });

        container.appendChild(clone);
    });
}

function openReviewPanel(panelName = "restaurant_reviews", id = null) {
    const panel = document.getElementById("panel");
    currentPanel = panelName;

    if (!id) {
        console.error("openReviewPanel 호출 시 id 없음");
        return;
    }

    const url = `/restaurant/${id}/reviews`;

    fetch(url)
        .then(res => res.text())
        .then(html => {
            panel.innerHTML = html;
            initPanelByName(panelName, id);
        })
        .catch(err => console.error(`${url} 로딩 실패`, err));
}


/* ---------------------------
3) 검색 실행 함수
---------------------------- */
function runSearch() {
    const keyword = document.getElementById("search_input").value.trim().toLowerCase();

    if (!keyword) {
        renderStoreList(storeData);  // 검색어 없으면 전체 출력
        return;
    }

    const filtered = storeData.filter(store =>
        store.name.toLowerCase().includes(keyword)
    );

    renderStoreList(filtered);
}


/* ---------------------------
4) 검색 패널 초기화 함수
---------------------------- */
function initSearchPanel() {
    const input = document.getElementById("search_input");
    const button = document.querySelector(".search_panel_search_button");

    // 엔터 입력 시 실행
    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            runSearch();
        }
    });

    // 검색 버튼 클릭 시 실행
    button.addEventListener("click", () => {
        runSearch();
    });

    // 패널 처음 열릴 때 전체 리스트 출력
    renderStoreList(storeData);
}

function openPopup(message, onConfirm) {
    const overlay = document.getElementById("globalPopup");
    const msgEl = document.getElementById("globalPopupMessage");
    const btn = document.getElementById("globalPopupConfirm");

    if (!overlay || !msgEl || !btn) return;

    msgEl.textContent = message;
    overlay.style.display = "flex";

    btn.onclick = () => {
    overlay.style.display = "none";
    if (typeof onConfirm === "function") {
        onConfirm();
    }
    };
}


// 페이지 로드되면 패널 열기
document.addEventListener("DOMContentLoaded", function () {
    panelButton();
});


// ㅇㅇ님 환영합니다. 텍스트 삽입
document.addEventListener("DOMContentLoaded", async function () {
    try {
        const res = await fetch("/api/user/");
        const data = await res.json();

        const nicknameEl = document.getElementById("nicknameArea");

        if (nicknameEl) {
            nicknameEl.innerText = `${data.nickname}님 환영합니다.`;
        }
    }
    catch(err) {
        console.error("닉네임 가져오기 실패:", err);
    }
});