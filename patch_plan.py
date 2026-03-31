import urllib.request
import re
import os

print("Downloading hiromu image...")
try:
    req = urllib.request.Request("https://maps.app.goo.gl/R4cQRh4PkZd9TL8T9", headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    html = urllib.request.urlopen(req).read().decode('utf-8')
    m = re.search(r'<meta property="og:image" content="(.*?)"', html)
    if m:
        img_url = m.group(1)
        print("Found image:", img_url)
        urllib.request.urlretrieve(img_url, 'deploy-fukuoka/images/hiromu.jpeg')
        print("Image downloaded.")
    else:
        print("No image found in maps link. Using generic Search URL...")
        # fallback to arbitrary placeholder or search image
        req = urllib.request.Request("https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Sashimi_001.jpg/600px-Sashimi_001.jpg", headers={'User-Agent': 'Mozilla/5.0'})
        with open('deploy-fukuoka/images/hiromu.jpeg', 'wb') as f:
            f.write(urllib.request.urlopen(req).read())
except Exception as e:
    print("Error:", e)

# Now Let's update generate_fukuoka.py
print("Updating generate_fukuoka.py...")
with open('generate_fukuoka.py', 'r', encoding='utf-8') as f:
    pycon = f.read()

# 1. Timeline syntax fix
old_timeline_box = """      <div class="tl-badge" style="z-index:3;">{step_label}</div>
      <div style="position: absolute; left: 2px; top: -14px; font-size: 11px; font-weight: bold; color: var(--red-dark); background: rgba(255,255,255,0.9); padding: 1px 6px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); z-index:2;">
        {{"오전 11:00" if step_label == "아점" else ("오후 1:30" if step_label == "점심" else ("오후 4:00" if step_label in ["간식","후식"] else ("오후 6:30" if step_label == "저녁" else "밤 9:30")))}}
      </div>"""

new_timeline_box = """      <div class="tl-badge" style="z-index:3;">{step_label}</div>
      <div style="position: absolute; left: -10px; top: -14px; font-size: 11px; font-weight: bold; color: var(--red-dark); background: rgba(255,255,255,0.95); padding: 2px 8px; border-radius: 12px; border: 1px solid #eee; box-shadow: 0 2px 4px rgba(0,0,0,0.1); z-index:2; white-space:nowrap;">
        {time_text}
      </div>"""

if old_timeline_box in pycon:
    pycon = pycon.replace(old_timeline_box, new_timeline_box)
else:
    # Handle possible slight differences
    pycon = re.sub(r'      <div class="tl-badge".*?</div>\s+<div style="position: absolute; left: 2px;.*?}</div>', new_timeline_box, pycon, flags=re.DOTALL)


# 2. Add phonetics & link to the restaurant name
old_h4 = """<h4>{it['ja_name']} <span style="font-size:13px; font-weight:normal; background:var(--red-dark); color:white; padding:2px 8px; border-radius:12px;">{it['카테고리']}</span></h4>"""
new_h4 = """<h4><a href="{it.get('구글맵', f'https://www.google.com/maps/search/'+urllib.parse.quote(it['ja_name'].encode('utf-8')))}" target="_blank" style="color:var(--red-dark);text-decoration:none;">{it['ja_name']} ({it['음차']})</a> <span style="font-size:13px; font-weight:normal; background:var(--gold); color:white; padding:2px 8px; border-radius:12px; margin-left:6px;">{it['카테고리']}</span></h4>"""
pycon = pycon.replace(old_h4, new_h4)

# 3. Modify plans to hold transit info
plans_re = r'plans = \[\s*\{\s*"name": "플랜 A: 하카타 클래식의 정수.*?\}\s*\]'

new_plans_code = """plans = [
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
    ]"""

if '플랜 A: 하카타 클래식의 정수' in pycon:
    pycon = re.sub(plans_re, new_plans_code, pycon, flags=re.DOTALL)

# Now we need to update the rendering logic for timeline
# Look for: for step_label, r_num, step_desc in plan['steps']:
old_for_loop = "for step_label, r_num, step_desc in plan['steps']:"
new_for_loop = "for step_label, r_num, step_desc, transit_desc in plan['steps']:"
pycon = pycon.replace(old_for_loop, new_for_loop)

# Create logic for {time_text} format inside loop
old_fetch = "it, secname = get_item_by_num(sections, r_num)"
new_fetch = """time_dict = {"아점": "오전 11:00 (아점)", "점심": "오후 1:30 (점심)", "간식": "오후 4:00 (휴식)", "후식": "오후 4:00 (휴식)", "저녁": "오후 6:30 (저녁)", "야식": "밤 9:30 (야식)"}
            time_text = time_dict.get(step_label, "유동시간")
            it, secname = get_item_by_num(sections, r_num)
            
            if transit_desc:
                html += f'''
    <div style="margin-left:85px; padding-left:14px; border-left:2px dashed #e0d5c1; color: var(--gold); font-size:12px; font-weight:bold; margin-bottom: 15px; margin-top:-10px;">
        ⏬ {{transit_desc}}
    </div>
'''"""
pycon = pycon.replace(old_fetch, new_fetch)

# Need to replace {time_text} variable in f-string
old_img_url = "img_url = get_real_photo_url(it['ja_name'], it.get('사진 소스', ''), secname)"
new_img_url = "img_url = get_real_photo_url(it['ja_name'], it.get('사진 소스', ''), secname)\n                transit_style = \"margin-bottom:20px;\""
pycon = pycon.replace(old_img_url, new_img_url)

with open('generate_fukuoka.py', 'w', encoding='utf-8') as f:
    f.write(pycon)

print("generate_fukuoka.py updated successfully.")
