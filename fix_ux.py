import urllib.request
import os

print("Downloading missing images...")
images = {
    "喰しん房松むら.jpeg": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=600&q=80",  # Sashimi
    "あじフライ食堂 かば.jpeg": "https://images.unsplash.com/photo-1628198622718-ef46754bc9f6?w=600&q=80",  # Fried dish / Tempura
    "hiromu.jpeg": "https://images.unsplash.com/photo-1553621042-f6e147245754?w=600&q=80"  # Dark Izakaya / meat
}
os.makedirs("deploy-fukuoka/images", exist_ok=True)
for filename, url in images.items():
    path = os.path.join("deploy-fukuoka", "images", filename)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with open(path, 'wb') as f:
            f.write(urllib.request.urlopen(req).read())
        print(f"Downloaded {filename}")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")

print("Updating generate_fukuoka.py...")
with open("generate_fukuoka.py", "r", encoding="utf-8") as f:
    pycon = f.read()

# 1. Double Brace FIX
pycon = pycon.replace("{{transit_desc}}", "{transit_desc}")

# 2. Skip empty sections in Tab 1
old_section_loop = """    for sec in sorted_sections:
        # anchor"""
new_section_loop = """    for sec in sorted_sections:
        if not sec['items']:
            continue
        # anchor"""
pycon = pycon.replace(old_section_loop, new_section_loop)

# 3. Add Top Button CSS & Accordion button CSS
# We will inject this before </style>
css_injection = """
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
if "/* Top Button */" not in pycon:
    pycon = pycon.replace("</style>", css_injection + "\n</style>")

# 4. Modify HTML Plan Generation to use Accordion Details
old_plan_html = """    for plan in plans:
        html += f'''
    <div class="plan-title">{plan['name']}</div>
    <p style="font-size:13px; color:#666; margin-bottom:20px;">{plan['desc']}</p>
    <div class="tl-container">
'''"""

# To make only the first accordion open by default, we can track the index using enumerate
# But we can just do python loop replace easily
# Let's replace the whole block dynamically
import re
new_plan_html = """    for i, plan in enumerate(plans):
        op = "open" if i == 0 else ""
        html += f'''
    <details class="plan-details" {op}>
        <summary class="plan-btn">{plan['name']}</summary>
        <div class="plan-desc">{plan['desc']}</div>
        <div class="tl-container" style="padding: 20px; padding-top:30px;">
'''"""
if 'class="plan-title"' in pycon:
    pycon = re.sub(r"    for plan in plans:\n        html \+= f'''\n    <div class=\"plan-title\">.*?<div class=\"tl-container\">\n'''", new_plan_html, pycon, flags=re.DOTALL)
    
    # Needs to close </details> after closing the tl-container inside the plan loop
    # look forward to the end of the plans loop in generate_fukuoka.py:
    #         html += '''
    #     </div>
    # '''
    # We replace it with:
    #         html += '''
    #     </div>
    #     </details>
    # '''
    pycon = re.sub(r"(html \+= '''\n    </div>\n''')", r"html += '''\n    </div>\n    </details>\n'''", pycon)


# 5. Add Top Button to Body & JS Logic
body_js = """<button onclick="window.scrollTo({top:0, behavior:'smooth'})" id="topBtn" title="Go to top">↑</button>
<script>
  // Top button visibility
  window.addEventListener('scroll', function() {
    var btn = document.getElementById("topBtn");
    if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {
      btn.style.display = "block";
    } else {
      btn.style.display = "none";
    }
  });"""
if "id=\"topBtn\"" not in pycon:
    pycon = pycon.replace("<script>", body_js)

with open("generate_fukuoka.py", "w", encoding="utf-8") as f:
    f.write(pycon)

print("generate_fukuoka.py strictly updated.")
