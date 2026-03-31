import re
import urllib.parse
import os

def parse_md():
    with open('plan/fukuoka-guide-34-spec.md', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    sections = []
    current_section = None
    current_item = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('### ') and not line.startswith('### 4.'):
            m = re.match(r'### (.+)', line)
            if m:
                if current_item:
                    current_section['items'].append(current_item)
                    current_item = None
                
                name_parts = m.group(1).split(' ')
                emoji = name_parts[0]
                name = ' '.join(name_parts[1:]).replace(' 섹션', '')
                current_section = {
                    'emoji': emoji,
                    'name': name,
                    'items': []
                }
                sections.append(current_section)
        elif line.startswith('#### No.'):
            if current_item and current_section:
                current_section['items'].append(current_item)
            
            m = re.match(r'#### No\.(\d+)\s*—\s*(.+)', line)
            if m:
                current_item = {
                    'num': m.group(1),
                    'ja_name': m.group(2).strip(),
                    'menu_items': []
                }
        elif current_item:
            if line.startswith('- **'):
                m = re.match(r'-\s*\*\*(.+?)\*\*\s*:\s*(.*)', line)
                if m:
                    key = m.group(1)
                    val = m.group(2)
                    if key == '시그니처 메뉴':
                        current_item['current_list'] = 'menu'
                    else:
                        current_item[key] = val
                        current_item['current_list'] = None
            elif line.startswith('- ') or line.startswith('  - '):
                clean_line = line.lstrip(' -')
                if current_item.get('current_list') == 'menu':
                    current_item['menu_items'].append(clean_line)
                    
    if current_item and current_section:
         current_section['items'].append(current_item)
         
    return sections

def get_photo_url(photo_src, sec_name):
    photo_src = photo_src.lower()
    mapping = [
        ('돈코츠', 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/Tonkotsu_ramen.JPG/600px-Tonkotsu_ramen.JPG'),
        ('중화소바', 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Shoyu_Ramen.jpg/600px-Shoyu_Ramen.jpg'),
        ('鶏白湯', 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Tori-paitan-ramen.jpg/600px-Tori-paitan-ramen.jpg'),
        ('백탕', 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Tori-paitan-ramen.jpg/600px-Tori-paitan-ramen.jpg'),
        ('味噌', 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Sapporo_Miso_Ramen.jpg/600px-Sapporo_Miso_Ramen.jpg'),
        ('미소', 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Sapporo_Miso_Ramen.jpg/600px-Sapporo_Miso_Ramen.jpg'),
        ('淡麗', 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Shoyu_Ramen.jpg/600px-Shoyu_Ramen.jpg'),
        ('수타', 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/Kitakata_ramen.jpg/600px-Kitakata_ramen.jpg'),
        ('ごぼう', 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Gobouten_udon.jpg/600px-Gobouten_udon.jpg'),
        ('우동', 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Udon.jpg/600px-Udon.jpg'),
        ('소바', 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Zaru-Soba.jpg/600px-Zaru-Soba.jpg'),
        ('とりかわ', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Cooking_yakitori.jpg/600px-Cooking_yakitori.jpg'),
        ('야키토리', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Cooking_yakitori.jpg/600px-Cooking_yakitori.jpg'),
        ('야키니쿠', 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Yakiniku_001.jpg/600px-Yakiniku_001.jpg'),
        ('냉면', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Naengmyeon.jpg/600px-Naengmyeon.jpg'),
        ('イカ', 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Ikasomen.jpg/600px-Ikasomen.jpg'),
        ('오징어', 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Ikasomen.jpg/600px-Ikasomen.jpg'),
        ('ごまさば', 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Gomasaba_001.jpg/600px-Gomasaba_001.jpg'),
        ('사시미', 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Sashimi_001.jpg/600px-Sashimi_001.jpg'),
        ('刺身', 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Sashimi_001.jpg/600px-Sashimi_001.jpg'),
        ('아지후라이', 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Aji_furai.jpg/600px-Aji_furai.jpg'),
        ('水炊き', 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Mizutaki_by_midorisyu_in_Fukuoka.jpg/600px-Mizutaki_by_midorisyu_in_Fukuoka.jpg'),
        ('스시', 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Sushi_platter.jpg/600px-Sushi_platter.jpg'),
        ('定食', 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Japanese_set_meal_001.jpg/600px-Japanese_set_meal_001.jpg'),
        ('정식', 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Japanese_set_meal_001.jpg/600px-Japanese_set_meal_001.jpg'),
        ('샤부샤부', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Shabu-shabu.jpg/600px-Shabu-shabu.jpg'),
        ('もつ鍋', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Motsunabe_002.jpg/600px-Motsunabe_002.jpg'),
        ('나베', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Motsunabe_002.jpg/600px-Motsunabe_002.jpg'),
        ('타코야키', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Takoyaki_001.jpg/600px-Takoyaki_001.jpg'),
        ('명태', 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/Mentaiko.jpg/600px-Mentaiko.jpg'),
        ('명란', 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/Mentaiko.jpg/600px-Mentaiko.jpg'),
        ('돈카츠', 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Tonkatsu_001.jpg/600px-Tonkatsu_001.jpg'),
        ('과자', 'https://cdn.pixabay.com/photo/2017/04/23/08/38/baking-2253258_1280.jpg'),
        ('파운드', 'https://cdn.pixabay.com/photo/2017/04/23/08/38/baking-2253258_1280.jpg'),
        ('카레', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Japanese_curry_001.jpg/600px-Japanese_curry_001.jpg')
    ]
    
    for key, url in mapping:
        if key in photo_src:
            return url
            
    sec_map = {
        '라멘': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/Tonkotsu_ramen.JPG/600px-Tonkotsu_ramen.JPG',
        '우동·소바': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Udon.jpg/600px-Udon.jpg',
        '야키토리·토리카와': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Cooking_yakitori.jpg/600px-Cooking_yakitori.jpg',
        '야키니쿠': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Yakiniku_001.jpg/600px-Yakiniku_001.jpg',
        '해산물·와쇼쿠': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Sushi_platter.jpg/600px-Sushi_platter.jpg',
        '나베·샤부샤부': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Motsunabe_002.jpg/600px-Motsunabe_002.jpg',
        '기타': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Japanese_set_meal_001.jpg/600px-Japanese_set_meal_001.jpg'
    }
    return sec_map.get(sec_name, 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Japanese_set_meal_001.jpg/600px-Japanese_set_meal_001.jpg')

def get_real_photo_url(ja_name, photo_src, sec_name):
    photo_file = f"{ja_name}.jpeg"
    photo_path = f"deploy-fukuoka/images/{photo_file}"
    if os.path.exists(photo_path):
        return f"images/{urllib.parse.quote(photo_file)}"
    return get_photo_url(photo_src, sec_name)

def build_card(item, sec_name):
    num = item.get('num', '')
    ja_name = item.get('ja_name', '')
    phonetic = item.get('음차', '')
    meaning = item.get('한자풀이', '')
    category = item.get('카테고리', '')
    special = item.get('특징', '')
    warn = item.get('주의', '')
    address = item.get('주소', '미확인')
    hours = item.get('영업시간', '미확인')
    closed = item.get('정기휴무', '미확인')
    transport = item.get('교통', '미확인')
    phone = item.get('전화', '미확인')
    visit_time = item.get('추천 방문시간', '')
    if not visit_time:
        if '점심' in category or '정식' in category:
            visit_time = '오후 12:00 ~ 2:00 (든든한 점심 식사)'
        elif '야키니쿠' in category or '나베' in category or '샤부샤부' in category:
            visit_time = '오후 6:30 ~ 8:30 (여유로운 저녁 식사)'
        elif '야키토리' in category or '이자카야' in category or '토리카와' in category:
            visit_time = '오후 7:00 ~ 10:00 (하루 일정을 마친 후 한 잔)'
        elif '우동' in category or '아지' in category:
            visit_time = '오전 11:30 ~ 1:30 (가벼운 아점 및 런치)'
        elif '카페' in category or '과자' in category or '디저트' in category:
            visit_time = '오후 2:30 ~ 4:30 (식후 디저트 및 휴식 타임)'
        elif '라멘' in category:
            visit_time = '밤 9:00 ~ 11:00 (든든한 야식 및 해장)'
        else:
            visit_time = '오후 1:00 ~ 2:00 또는 오후 6:00 ~ 7:00'
            
    photo_src = item.get('사진 소스', '')
    mapUrl = item.get('구글맵', '')
    
    photo = get_real_photo_url(ja_name, photo_src, sec_name)
    
    if address == '미확인':
        address = '<span style="color:#d9534f;font-weight:bold;">정보 확인 중 — 방문 전 구글맵 검색 권장</span>'
    if hours == '미확인':
        hours = '<span style="color:#d9534f;font-weight:bold;">전화 확인 권장</span>'
        
    if 'hiromu' in ja_name.lower() or 'isozaki' in ja_name.lower():
        warn = '이전 이름이나 현지 영업 여부를 구글맵 링크로 꼭 확인하세요!'
        
    menus_html = ""
    for menu in item.get('menu_items', []):
        m_name = menu
        m_phon = ""
        m_price = ""
        m_desc = ""
        
        m_match = re.search(r'¥[\d,]+(?:~/인|~\/본|~/본|~)?', menu)
        if m_match:
            m_price = m_match.group(0)
            menu = menu.replace(m_price, '').strip()
            
        m_match2 = re.match(r'^(.+?)(?:\s*\((.+?)\))?(?:\s*—\s*(.+))?$', menu)
        if m_match2:
            m_name = m_match2.group(1).strip()
            m_phon = m_match2.group(2) if m_match2.group(2) else ""
            m_desc = m_match2.group(3) if m_match2.group(3) else ""
        
        phon_tag = f'<span class="menu-phonetic">({m_phon})</span>' if m_phon else ""
        price_tag = f'<span class="menu-price">{m_price}</span>' if m_price else ""
        desc_tag = f'<span class="menu-desc">{m_desc}</span>' if m_desc else ""
        
        menus_html += f"""
<li class="menu-item">
<span class="menu-name">{m_name} {phon_tag}</span>
{price_tag}
{desc_tag}
</li>"""

    enc_name = urllib.parse.quote(ja_name.encode('utf-8'))
    enc_addr = urllib.parse.quote(address.split('<')[0].strip().encode('utf-8'))
    
    map_btn = f'<a class="map-btn" href="{mapUrl}" target="_blank">📍 구글맵에서 보기</a>' if mapUrl else f'<a class="map-btn" href="https://www.google.com/maps/search/{enc_name}+{enc_addr}" target="_blank">📍 구글맵에서 보기</a>'
    
    html = f"""
<!-- {num}. {ja_name} -->
<div class="rest-card">
  <div class="rest-head">
    <span class="rest-num">{num}</span>
    <div class="rest-names">
      <div class="rest-ja">{ja_name}</div>
      <div class="rest-phonetic">{phonetic}</div>
      <div class="rest-meaning">{meaning}</div>
      <span class="rest-category">{category}</span>
    </div>
  </div>

  <img class="food-photo"
    src="{photo}"
    alt="{ja_name}"
    loading="lazy"
    onerror="this.src='https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Japanese_set_meal_001.jpg/600px-Japanese_set_meal_001.jpg'">
"""
    if special:
        html += f"""
  <div class="special-box">
    <strong>왜 특별한가:</strong> {special}
  </div>
"""

    html += f"""
  <div class="info-section">
    <div class="info-title">시그니처 메뉴</div>
    <ul class="menu-list">
      {menus_html}
    </ul>
  </div>

  <div class="info-section">
    <div class="info-title">영업 정보</div>
    <div class="info-row"><span class="info-label">영업시간</span><span class="info-val">{hours}</span></div>
    <div class="info-row"><span class="info-label">정기휴무</span><span class="info-val">{closed}</span></div>
    <div class="info-row"><span class="info-label">주소</span><span class="info-val">{address}</span></div>
    <div class="info-row"><span class="info-label">교통</span><span class="info-val">{transport}</span></div>
    <div class="info-row"><span class="info-label">전화</span><span class="info-val">{phone}</span></div>"""
    
    if visit_time:
        html += f"""    <div class="info-row"><span class="info-label" style="color:var(--red-mid);font-weight:bold">추천시간</span><span class="info-val" style="color:var(--red-dark);font-weight:bold">{visit_time}</span></div>"""
        
    html += """
  </div>
"""
    if warn:
        html += f"""
  <div class="warn-box">
    ⚠️ <strong>주의:</strong> {warn}
  </div>
"""

    html += f"""
  {map_btn}
</div>
"""
    return html

def get_item_by_num(sections, num):
    for sec in sections:
        for it in sec['items']:
            if it.get('num') == str(num):
                return it, sec['name']
    return None, None

def generate_html(sections):
    with open('fukuoka-food-guide.html', 'r', encoding='utf-8') as f:
        ref_content = f.read()
        
    style_start = ref_content.find('<style>')
    style_end = ref_content.find('</style>') + len('</style>')
    style_block = ref_content[style_start:style_end]
    
    html = "<!DOCTYPE html>\n<html lang=\"ko\">\n<head>\n<meta charset=\"UTF-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n<title>후쿠오카 하카타 현지 맛집 가이드</title>\n"
    html += style_block
    
    extra_css = """
<style>
.tab-buttons {
    display: flex; gap: 10px; margin: 20px auto; justify-content: center; flex-wrap: wrap; margin-bottom: 30px;
}
.tab-btn {
    padding: 12px 24px; border: 2px solid var(--red-dark); background: white; border-radius: 30px; cursor: pointer; font-size: 16px; font-weight: bold; color: var(--red-dark); transition: 0.3s;
}
.tab-btn.active, .tab-btn:hover {
    background: var(--red-dark); color: white;
}
.tab-content {
    display: none; animation: fadeIn 0.4s;
}
.tab-content.active {
    display: block;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* Timeline UI for Plans */
.plan-container {
    background: white; border-radius: 12px; padding: 25px; margin-bottom: 40px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
}
.plan-header {
    font-size: 22px; color: var(--red-dark); border-bottom: 2px solid #f0e6d2; padding-bottom: 10px; margin-bottom: 25px; font-weight:bold;
}
.timeline {
    position: relative; max-width: 800px; margin: 0 auto;
}
.timeline::before {
    content: ''; position: absolute; left: 18px; top: 0; bottom: 0; width: 4px; background: #e0d5c1; border-radius: 4px; z-index: 1;
}
.rest-grid {
    display:grid; grid-template-columns:repeat(auto-fill, minmax(340px,1fr)); gap:0;
}
.rest-card {
    padding:22px 20px 24px;
    background: #ffffff !important;
    border-radius: 12px;
    margin: 10px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    color: #222 !important;
}
.rest-card .special-box { background: rgba(180,60,20,0.05); color: #333; }
.rest-card .warn-box { background: rgba(200,150,0,0.05); color: #444; }
.rest-card .enjoy-box { background: rgba(30,80,30,0.05); color: #333; }
.rest-card .info-title { color: var(--red-dark); }
.rest-card *:not(.map-btn) { color: inherit; }
.map-btn {
    display:inline-flex; align-items:center; gap:6px;
    background:var(--red-dark); color:#ffffff !important;
    padding:7px 16px; border-radius:20px;
    text-decoration:none; font-size:12px; font-weight:bold;
    transition:background .2s; margin-top:4px;
}
.rest-card .menu-desc { color: #555; }
.tl-item {
    position: relative; padding-left: 60px; margin-bottom: 30px;
}
.tl-badge {
    position: absolute; left: 0; top: 0; width: 40px; height: 40px; background: var(--gold); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 13px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); z-index: 2; border: 2px solid white;
}
.tl-content {
    background: #faf8f5; border-radius: 12px; padding: 15px; border-left: 4px solid var(--red-dark); display: flex; gap: 15px; align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.03); flex-wrap: wrap;
}
.tl-img {
    width: 80px; height: 80px; object-fit: cover; border-radius: 8px; flex-shrink: 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.tl-info { flex-grow: 1; }
.tl-info h4 { margin: 0 0 5px 0; color: #333; font-size: 18px; display:flex; align-items:center; gap:8px; }
.tl-info p { margin: 0; font-size: 14px; color: #666; line-height: 1.4; }
.tl-desc { background: white; padding: 8px 12px; border-radius: 6px; font-size:13px; color:#444; border: 1px dashed #d5c8b5; margin-top:8px; width: 100%;}
@media (max-width: 600px) {
    .tl-content { flex-direction: column; align-items: flex-start; }
    .tl-img { width: 100%; height: 140px; }
}

/* For time based section */
.time-group-title {
    background: var(--red-dark); color: white; display: inline-block; padding: 8px 20px; border-radius: 20px; font-size: 18px; margin: 30px 0 15px 0; box-shadow: 0 3px 6px rgba(0,0,0,0.1);
}

  /* Top Button */
  #topBtn {
    display: none; position: fixed; bottom: 30px; right: 30px; z-index: 999;
    font-size: 18px; border: none; outline: none; background-color: var(--red-dark);
    color: white; cursor: pointer; padding: 15px; border-radius: 50%;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3); transition: background-color 0.3s;
    width: 50px; height: 50px; text-align: center; line-height: 20px;
  }
  #topBtn:hover { background-color: var(--red-mid); }
  
  /* Plan Accordion Button Style */
  details.plan-details {
    margin-bottom: 24px;
    background: var(--g-light);
    border-radius: 12px;
    box-shadow: var(--g-shadow);
    overflow: hidden;
  }
  summary.plan-btn {
    list-style: none; /* remove default triangle */
    background: linear-gradient(135deg, var(--red-dark) 0%, #a33030 100%);
    color: white; padding: 16px 20px; cursor: pointer;
    font-size: 16px; font-weight: bold; position: relative;
    user-select: none; transition: background 0.2s;
  }
  summary.plan-btn::-webkit-details-marker { display: none; }
  summary.plan-btn::after {
    content: '+'; position: absolute; right: 20px; top: 50%;
    transform: translateY(-50%); font-size: 20px; font-weight: bold;
  }
  details[open] summary.plan-btn::after {
    content: '-';
  }
  details[open] summary.plan-btn {
    border-bottom: 3px solid var(--gold);
  }
  .plan-desc {
    padding: 12px 20px; font-size: 14px; color: #444; background: #fffdfa;
    border-bottom: 1px solid #eee;
  }

"""
    style_block = style_block.replace("</style>", extra_css + "</style>")
    
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>후쿠오카 현지인 추천 맛집 가이드 – 34선</title>
{style_block}
<button onclick="window.scrollTo({{top:0, behavior:'smooth'}})" id="topBtn" title="Go to top">↑</button>
<script>
  // Top button visibility
  window.addEventListener('scroll', function() {{
    var btn = document.getElementById("topBtn");
    if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {{
      btn.style.display = "block";
    }} else {{
      btn.style.display = "none";
    }}
  }});
function openTab(tabId) {{
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    event.currentTarget.classList.add('active');
}}
</script>
</head>
<body>

<nav>
  <ul>
    <li><a href="#ramen" onclick="openTab('tab-all')">🍜 라멘</a></li>
    <li><a href="#udon" onclick="openTab('tab-all')">🍵 우동·소바</a></li>
    <li><a href="#yakitori" onclick="openTab('tab-all')">🍢 야키토리·토리카와</a></li>
    <li><a href="#yakiniku" onclick="openTab('tab-all')">🥩 야키니쿠</a></li>
    <li><a href="#kaisenwa" onclick="openTab('tab-all')">🐟 해산물·와쇼쿠</a></li>
    <li><a href="#nabe" onclick="openTab('tab-all')">🫕 나베·샤부샤부</a></li>
    <li><a href="#etc" onclick="openTab('tab-all')">🎯 기타</a></li>
  </ul>
</nav>

<div class="hero">
  <h1>후쿠오카 현지인 맛집 가이드</h1>
  <p>라멘부터 야키토리까지 — 현지인이 실제 가는 하카타 34선</p>
  <div class="badges">
    <span class="badge">🇯🇵 현지인 추천</span>
    <span class="badge">📍 하카타·텐진</span>
    <span class="badge">✅ 영업 확인</span>
    <span class="badge">💴 엔화 현금 필수</span>
  </div>
</div>

<div class="container">

<div class="tab-buttons">
  <button class="tab-btn active" onclick="openTab('tab-all')">🍽️ 전체 맛집 보기</button>
  <button class="tab-btn" onclick="openTab('tab-time')">⏰ 시간대별 추천</button>
  <button class="tab-btn" onclick="openTab('tab-plans')">🧭 하루 5끼 미식 플랜</button>
</div>

<!-- ==========================================
     TAB 1: 전체 식당
     ========================================== -->
<div id="tab-all" class="tab-content active">
"""

    section_id_map = {
        '라멘': 'ramen', '우동·소바': 'udon', '야키토리·토리카와': 'yakitori',
        '야키니쿠': 'yakiniku', '해산물·와쇼쿠': 'kaisenwa', '나베·샤부샤부': 'nabe', '기타': 'etc'
    }
    
    for idx, sec in enumerate(sections):
        if not sec['name']: continue
        s_id = section_id_map.get(sec['name'], f"sec-{idx}")
        html += f"""
<div class="section-header" id="{s_id}">
  <span style="font-size:20px">{sec['emoji']}</span>
  <h2>{sec['name']}</h2>
</div>
<div class="section-body">
<div class="rest-grid">
"""
        for item in sec['items']:
            html += build_card(item, sec['name'])
        html += "</div></div>\n"

    html += """
</div> <!-- END TAB 1 -->
"""

    # ==========================================
    # TAB 2: 시간대별 분류
    # ==========================================
    time_groups = {
        '🌅 아침메뉴 (브런치/11시전후)': [33, 28, 1, 17, 31, 23, 29, 30, 14],
        '☀️ 점심/오후 (점심겸저녁)': [8, 9, 32, 11, 25, 21, 5, 10],
        '🌙 저녁메뉴 (일반 식사/반주)': [27, 16, 2, 6, 19, 3, 24],
        '🌃 야식메뉴 (심야/2차 특화)': [4, 22, 26, 13, 18, 20, 34, 7, 15, 12]
    }
    
    html += '<div id="tab-time" class="tab-content">\n'
    for title, nums in time_groups.items():
        html += f'<div class="time-group-title">{title}</div>\n<div class="rest-grid">\n'
        for num in nums:
            it, secname = get_item_by_num(sections, num)
            if it:
                html += build_card(it, secname)
        html += '</div>\n'
    html += '</div> <!-- END TAB 2 -->\n'


    # ==========================================
    # TAB 3: 동선을 고려한 하루 5끼 식사 플랜
    # ==========================================
    plans = [
        {
            "name": "플랜 A: 하카타 클래식의 정수 (전통과 근본 코스)",
            "desc": "하카타를 대표하는 명물(우동, 카레, 생선, 야키니쿠, 라멘)을 정석대로 밟는 절대 실패 없는 코스.",
            "steps": [
                ("아점", 17, "맑고 보들보들한 전형적인 하카타 우동으로 부드럽게 시작", ""),
                ("점심", 30, "현지인 열광! 그날 들어온 40여 종의 펄떡이는 생선 정식", "🚇 지하철로 텐진미나미/와타나베도리 이동 (약 15분)"),
                ("간식", 33, "골목 진입부터 향기로운 후쿠오카 넘버원 스파이스 카레", "🚶‍♂️ 와타나베도리 골목 안쪽으로 도보 산책 (약 10분)"),
                ("저녁", 21, "육즙 가득 야키니쿠와 하카타 냉면 원조의 황홀한 만남", "🚇 나카스가와바타 방면으로 나카스 강변을 따라 도보 이동 (약 15분)"),
                ("야식", 23, "마무리는 역시 진하디 진한 하카타 돈코츠 라멘 총본점", "🚇 지하철이나 버스로 다시 하카타역 복귀 (약 15분)")
            ]
        },
        {
            "name": "플랜 B: 국물과 면 매니아의 순례길 (면식 수행 코스)",
            "desc": "면과 국물 요리의 끝판왕. 하얀 돈카츠와 디저트로 변주를 즐기는 완벽한 코스.",
            "steps": [
                ("아점", 9, "시라카와 발상, 후루룩 넘어가는 손반죽 수타 추카소바", ""),
                ("점심", 28, "오랜 저온 조리로 완성되는 화제의 '하얀 돈카츠'", "🚇 롯폰마츠에서 텐진으로 지하철/버스 이동 (약 20분)"),
                ("후식", 32, "여성 쉐프가 구워내는 사랑스러운 구움과자 한 조각", "🚶‍♂️ 야쿠인역 근방으로 소화시킬 겸 도보 및 버스 (약 15분)"),
                ("저녁", 27, "100년 역사가 끓여낸 뽀얗고 깊은 도리 미즈타키 전골", "🚇 다시 텐진 중심가 텐진빌딩으로 이동 (약 10분)"),
                ("야식", 20, "6일간 정성스레 구워져 나오는 바삭쫄깃 토리카와 꼬치", "🚇 텐진에서 기온 방향으로 택시나 지하철 이동 (약 15분)")
            ]
        },
        {
            "name": "플랜 C: 궁극의 해산물 & 로컬 감성 (바다 요리와 현지풍)",
            "desc": "해산물과 로컬 선술집(이자카야) 감성을 듬뿍 느끼는 코스.",
            "steps": [
                ("아점", 14, "아침부터 줄 서는 신선하고 두툼한 전갱이(아지) 튀김 정식", ""),
                ("점심", 29, "1,050엔이라는 기적 같은 가성비의 신선한 스시 정식 런치", "🚇 벳푸/야쿠인오도리 방면에서 와타나베도리로 버스 이동 (약 20분)"),
                ("간식", 8, "웨이팅 필수! 부드럽고 담백한 닭백탕 토리소바 한 그릇", "🚇 와타나베도리에서 고후쿠마치/나카스 쪽으로 이동 (약 15분)"),
                ("저녁", 5, "수조에서 갓 건진 요부코 활오징어와 참깨 고등어", "🚇 나카스에서 오호리공원역으로 공항선 환승 이동 (약 20분)"),
                ("야식", 4, "술이 확 깨버리는 강렬한 감칠맛의 심야 산라탕면", "🚇 오호리공원에서 고후쿠마치로 다시 심야 이동 (택시 타거나 막차 지하철)")
            ]
        },
        {
            "name": "플랜 D: 후쿠오카 프리미엄 미식 여정 (고급스러운 경험)",
            "desc": "조금 더 고급스럽고, 조금 더 우아하게 즐기는 프리미엄 식도락 일정.",
            "steps": [
                ("아점", 3, "유형문화재 지정 목조건물에서 고즈넉하게 즐기는 수타 소바", ""),
                ("점심", 6, "화제의 이나치카, 눈과 입이 즐거운 고급 도미 오차즈케 세트", "🚶‍♂️ 다이묘에서 텐진 지하 이나치카로 도보 이동 (약 10분)"),
                ("간식", 1, "아담하지만 강렬한, 정통 장인이 빚은 수타 우엉우동", "🚶‍♂️ 다시 아카사카/다이묘 방면으로 가볍게 걷기 (약 10분)"),
                ("저녁", 19, "박다역 시티뷰와 함께하는 프라이빗 마블링 흑모와규 샤부샤부", "🚇 텐진이나 아카사카에서 하카타역으로 지하철 공항선 (약 15분)"),
                ("야식", 13, "재료 본연의 맛을 살린 어른을 위한 미야자키 닭 숯불구이", "🚇 하카타역에서 나카스카와바타로 택시 또는 지하철 이동 (약 10분)")
            ]
        }
    ]

    html += '<div id="tab-plans" class="tab-content">\n'
    for plan in plans:
        html += f'''
<div class="plan-container">
  <div class="plan-header">{plan['name']}</div>
  <p style="color:#666; margin-bottom: 25px;">{plan['desc']}</p>
  <div class="timeline">
'''
        for step_label, r_num, step_desc, transit_desc in plan['steps']:
            time_dict = {"아점": "오전 11:00 (아점)", "점심": "오후 1:30 (점심)", "간식": "오후 4:00 (휴식)", "후식": "오후 4:00 (휴식)", "저녁": "오후 6:30 (저녁)", "야식": "밤 9:30 (야식)"}
            time_text = time_dict.get(step_label, "유동시간")
            it, secname = get_item_by_num(sections, r_num)
            
            if transit_desc:
                html += f'''
    <div style="margin-left:85px; padding-left:14px; border-left:2px dashed #e0d5c1; color: var(--gold); font-size:12px; font-weight:bold; margin-bottom: 15px; margin-top:-10px;">
        ⏬ {transit_desc}
    </div>
'''
            if it:
                img_url = get_real_photo_url(it['ja_name'], it.get('사진 소스', ''), secname)
                transit_style = "margin-bottom:20px;"
                html += f'''
    <div class="tl-item">
      <div class="tl-badge" style="z-index:3;">{step_label}</div>
      <div style="position: absolute; left: -10px; top: -14px; font-size: 11px; font-weight: bold; color: var(--red-dark); background: rgba(255,255,255,0.95); padding: 2px 8px; border-radius: 12px; border: 1px solid #eee; box-shadow: 0 2px 4px rgba(0,0,0,0.1); z-index:2; white-space:nowrap;">
        {time_text}
      </div>
      <div class="tl-content">
        <img src="{img_url}" class="tl-img" alt="{it['ja_name']}">
        <div class="tl-info">
          <h4><a href="{it.get('구글맵', f'https://www.google.com/maps/search/'+urllib.parse.quote(it['ja_name'].encode('utf-8')))}" target="_blank" style="color:var(--red-dark);text-decoration:none;">{it['ja_name']} ({it['음차']})</a> <span style="font-size:13px; font-weight:normal; background:var(--gold); color:white; padding:2px 8px; border-radius:12px; margin-left:6px;">{it['카테고리']}</span></h4>
          <p><strong>시그니처:</strong> {it.get('menu_items', [''])[0].split('—')[0].split('¥')[0]}</p>
          <div class="tl-desc">✨ {step_desc}</div>
        </div>
      </div>
    </div>
'''
        html += '''
  </div>
</div>
'''
    html += '</div> <!-- END TAB 3 -->\n'

    html += """
</div> <!-- container end -->
<footer>
  <p>이 가이드는 현지 정보 및 최신 데이터를 바탕으로 작성되었습니다.</p>
</footer>
</body>
</html>
"""

    with open('fukuoka-guide-34.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    with open('deploy-fukuoka/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
        
    print("Successfully generated fukuoka-guide-34.html with complete Tab features")

if __name__ == '__main__':
    sections = parse_md()
    generate_html(sections)
