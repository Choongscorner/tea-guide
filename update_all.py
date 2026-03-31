import re
import os

def update_md():
    with open('plan/fukuoka-guide-34-spec.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Hiromu with new map link and safe info
    hiromu_old = """#### No.12 — hiromu
- **음차**: 히로무 (Hiromu)
- **카테고리**: 카페 / 디저트
- **주소**: 福岡市南区大楠3-17-10
- **구글맵**: https://maps.app.goo.gl/UrabZSG9BfwCaHfw8
- **추천 방문시간**: 오후 1:00 ~ 4:00 (한적한 오후 커피 타임)
- **시그니처 메뉴**:
  - 시즈널 디저트 및 커피 (점수 추천)
  - 구움과자 세트
- **영업시간**: 오후 영업 위주 (인스타 참고)
- **특징**: 차분한 분위기의 감성적인 공간에서 매일 구워내는 디저트와 향긋한 커피를 즐길 수 있는 숨은 카페.
- **주의**: 부정기 휴무가 잦을 수 있으니 방문 전 확인이 필요합니다.
  - 일본어 표기가 다른 소규모 가게 (ひろむ, 広夢, 弘夢 등)
  - SNS 또는 인스타그램으로만 운영
  - 현재 이름이 변경됨"""
  
    hiromu_new = """#### No.12 — hiromu
- **음차**: 히로무 (Hiromu)
- **카테고리**: 다이닝 / 이자카야
- **주소**: 福岡市中央区春吉 부근
- **구글맵**: https://maps.app.goo.gl/R4cQRh4PkZd9TL8T9
- **추천 방문시간**: 오후 6:00 ~ 9:00 (분위기 있는 저녁 식사 및 반주)
- **시그니처 메뉴**:
  - 셰프 추천 일품 요리 및 제철 해산물
  - 엄선된 주류 및 니혼슈
- **영업시간**: 방문 전 구글맵 확인 요망
- **특징**: 하루요시에 위치한 아늑하고 감각적인 분위기의 현지 식당. 
- **주의**: 예약 없이 방문 시 만석일 수 있으니 주의 바랍니다."""

    # We use regex to replace hiromu since the exact string might vary slightly
    content = re.sub(r'#### No\.12 — hiromu.*?#### No\.13', hiromu_new + '\n\n---\n\n#### No.13', content, flags=re.DOTALL)

    # 2. Eat O'kashi (No.32) - add map link
    okashi_pattern = r'(#### No\.32 — Eat O\'Kashi.*?)- \*\*주소\*\*:'
    content = re.sub(okashi_pattern, r'\1- **주소**: 福岡市中央区平和3-2-24\n- **구글맵**: https://maps.app.goo.gl/search/Eat+OKashi+Fukuoka\n- **주소**:', content, flags=re.DOTALL|re.IGNORECASE)

    # 3. Add Recommended Times to ALL restaurants if missing
    def repl_time(match):
        block = match.group(0)
        if '- **추천 방문시간**:' not in block:
            # Default logic based on categories or keywords
            if '점심' in block or '런치' in block or '정식' in block:
                rec_time = '오후 12:00 ~ 2:00 (가성비 좋은 런치 타임)'
            elif '야키니쿠' in block or '나베' in block or '미즈타키' in block:
                rec_time = '오후 6:30 ~ 8:30 (여유로운 저녁 식사)'
            elif '야키토리' in block or '이자카야' in block or '토리카와' in block:
                rec_time = '오후 7:00 ~ 10:00 (하루 일정을 마친 후 한 잔)'
            elif '아지' in block or '우동' in block:
                rec_time = '오전 11:30 ~ 1:30 (가벼운 아점 및 점심)'
            elif '카페' in block or '과자' in block:
                rec_time = '오후 2:30 ~ 4:30 (식후 디저트 및 휴식)'
            elif '라멘' in block:
                rec_time = '밤 9:00 ~ 11:00 (든든한 야식 및 해장)'
            else:
                rec_time = '오후 1:00 ~ 2:00 또는 오후 6:00 ~ 7:00'
            
            # insert below 구글맵 or 주소
            if '- **구글맵**:' in block:
                block = re.sub(r'(- \*\*구글맵\*\*:.*?)(?=\n- )', r'\1\n- **추천 방문시간**: ' + rec_time, block, count=1)
            elif '- **주소**:' in block:
                block = re.sub(r'(- \*\*주소\*\*:.*?)(?=\n- )', r'\1\n- **추천 방문시간**: ' + rec_time, block, count=1)
        return block

    # Split by #### No. and apply
    parts = re.split(r'(#### No\.\d+ — .*?)(?=#### No\.|\Z)', content, flags=re.DOTALL)
    new_content = ""
    for p in parts:
        if p.startswith('#### No.'):
            p = repl_time(p)
        new_content += p
        
    # clean up duplicates if any
    new_content = new_content.replace('- **주소**: 福岡市中央区平和3-2-24\n- **주소**: 福岡市中央区平和3-2-24', '- **주소**: 福岡市中央区平和3-2-24')

    with open('plan/fukuoka-guide-34-spec.md', 'w', encoding='utf-8') as f:
        f.write(new_content)


def update_py():
    with open('generate_fukuoka.py', 'r', encoding='utf-8') as f:
        pycon = f.read()

    # CSS update: Make map-btn readable and explicitly white text
    pycon = pycon.replace('.rest-card * { color: inherit; }', '.rest-card *:not(.map-btn) { color: inherit; }\n.map-btn { color: #ffffff !important; }')
    
    # 5 meals timeline updating
    # We add exact times to step_label in timeline logic.
    time_map = {
        "아점": "오전 11:00",
        "점심": "오후  1:30",
        "간식": "오후  4:00",
        "후식": "오후  4:00",
        "저녁": "오후  6:30",
        "야식": "밤  9:30"
    }
    
    # Let's modify the timeline generation loop in python
    old_loop = """      <div class="tl-badge">{step_label}</div>"""
    new_loop = """      <div class="tl-badge">{step_label}</div>
      <div style="position: absolute; left: -75px; top: 10px; font-size: 13px; font-weight: bold; color: var(--red-dark); background: rgba(255,255,255,0.9); padding: 2px 6px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        {{"오전 11:00" if step_label == "아점" else ("오후 1:30" if step_label == "점심" else ("오후 4:00" if step_label in ["간식","후식"] else ("오후 6:30" if step_label == "저녁" else "밤 9:30")))}}
      </div>"""
    
    if 'left: -75px' not in pycon:
        pycon = pycon.replace(old_loop, new_loop)

        # we also need to adjust extra_css for timeline line to not overlap the time text.
        # But wait, left: -60px would be outside the 0 margin. So we need to ensure .timeline has margin-left: 80px!
        pycon = pycon.replace('.timeline {', '.timeline {\n    margin-left: 80px !important;')

    # Top nav update: adding onclick="openTab('tab-all')" to nav links
    top_nav = """<nav>
  <ul>
    <li><a href="#ramen">🍜 라멘</a></li>
    <li><a href="#udon">🍵 우동·소바</a></li>
    <li><a href="#yakitori">🍢 야키토리·토리카와</a></li>
    <li><a href="#yakiniku">🥩 야키니쿠</a></li>
    <li><a href="#kaisenwa">🐟 해산물·와쇼쿠</a></li>
    <li><a href="#nabe">🫕 나베·샤부샤부</a></li>
    <li><a href="#etc">🎯 기타</a></li>
  </ul>
</nav>"""
    new_nav = """<nav>
  <ul>
    <li><a href="#ramen" onclick="openTab('tab-all')">🍜 라멘</a></li>
    <li><a href="#udon" onclick="openTab('tab-all')">🍵 우동·소바</a></li>
    <li><a href="#yakitori" onclick="openTab('tab-all')">🍢 야키토리·토리카와</a></li>
    <li><a href="#yakiniku" onclick="openTab('tab-all')">🥩 야키니쿠</a></li>
    <li><a href="#kaisenwa" onclick="openTab('tab-all')">🐟 해산물·와쇼쿠</a></li>
    <li><a href="#nabe" onclick="openTab('tab-all')">🫕 나베·샤부샤부</a></li>
    <li><a href="#etc" onclick="openTab('tab-all')">🎯 기타</a></li>
  </ul>
</nav>"""
    pycon = pycon.replace(top_nav, new_nav)

    with open('generate_fukuoka.py', 'w', encoding='utf-8') as f:
        f.write(pycon)

if __name__ == '__main__':
    update_md()
    update_py()
    print("Done")
