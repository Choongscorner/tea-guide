import re

with open("generate_fukuoka.py", "r", encoding="utf-8") as f:
    text = f.read()

# Fix double curly braces inside the injected JS snippet
bad_js = """<button onclick="window.scrollTo({top:0, behavior:'smooth'})" id="topBtn" title="Go to top">↑</button>
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

good_js = """<button onclick="window.scrollTo({{top:0, behavior:'smooth'}})" id="topBtn" title="Go to top">↑</button>
<script>
  // Top button visibility
  window.addEventListener('scroll', function() {{
    var btn = document.getElementById("topBtn");
    if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {{
      btn.style.display = "block";
    }} else {{
      btn.style.display = "none";
    }}
  }});"""

text = text.replace(bad_js, good_js)

with open("generate_fukuoka.py", "w", encoding="utf-8") as f:
    f.write(text)

print("generate_fukuoka.py javascript f-string escaped correctly!")
