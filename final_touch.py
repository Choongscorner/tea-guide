import os
import re

# 1. Print current images
print("Existing images in deploy-fukuoka/images:")
print(os.listdir('deploy-fukuoka/images'))

with open('plan/fukuoka-guide-34-spec.md', 'r', encoding='utf-8') as f:
    spec = f.read()

# Let's inspect ja_names simply
ja_names = []
for line in spec.split('\n'):
    if line.startswith("- **식당명**"):
        # e.g. - **식당명**: 쿠이신보 마츠무라 (喰しん房松むら)
        m = re.search(r'\((.*?)\)', line)
        if m:
            ja_names.append(m.group(1))

print("Extracted Some ja_names:", [n for n in ja_names if "hiromu" in n or "松むら" in n or "かば" in n])

# 2. Patch generate_fukuoka.py
with open('generate_fukuoka.py', 'r', encoding='utf-8') as f:
    pycon = f.read()

# Fix 1: skip empty sections in Tab 1
old_section_loop = """    for sec in sorted_sections:
        # anchor"""
new_section_loop = """    for sec in sorted_sections:
        if not sec['items']:
            continue
        if "카드 구성 순서" in sec['name'] or "URL 버튼" in sec['name']:
            continue
        # anchor"""
pycon = pycon.replace(old_section_loop, new_section_loop)

# Fix 2: Accordion for plans
old_plan_html = """    for plan in plans:
        html += f'''
    <div class="plan-title">{plan['name']}</div>
    <p style="font-size:13px; color:#666; margin-bottom:20px;">{plan['desc']}</p>
    <div class="tl-container">
'''"""
new_plan_html = """    for i, plan in enumerate(plans):
        op = "open" if i == 0 else ""
        html += f'''
    <details class="plan-details" {op}>
        <summary class="plan-btn">{plan['name']}</summary>
        <div class="plan-desc">{plan['desc']}</div>
        <div class="tl-container" style="padding: 20px; padding-top:30px;">
'''"""
pycon = pycon.replace(old_plan_html, new_plan_html)

# End of plan loop details
# Need to replace the `</div>` at the end of the `for step_...` loop with `</div></details>`
old_plan_end = """        html += '''
    </div>
'''"""
new_plan_end = """        html += '''
    </div>
    </details>
'''"""
# We must be careful to only replace the one inside the plans loop, which is exactly `    </div>\n'''`
pycon = re.sub(r"        html \+= '''\n    </div>\n'''", new_plan_end, pycon, count=1)

with open('generate_fukuoka.py', 'w', encoding='utf-8') as f:
    f.write(pycon)

print("generate_fukuoka.py patched!")

