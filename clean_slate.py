import re

with open("generate_fukuoka.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
skip = False
for line in lines:
    if "style_end = ref_content.find('" in line and "/* Top Button */" in line:
        skip = True
        out.append("    style_end = ref_content.find('</style>') + len('</style>')\n")
        out.append("    style_block = ref_content[style_start:style_end]\n")
        out.append("    html += style_block\n")
        continue

    if skip:
        if "extra_css = " in line and '"""' in line:
            skip = False
            out.append(line)
        elif "html += f" in line and "<style>" in line:
            skip = False
            out.append(line)
        elif "style_block = style_block.replace('" in line:
            # We are inside the second broken block, we just keep skipping until we hit extra_css
            pass
        elif "extra_css = " in line and '"""\n' in line:
            skip=False
            out.append(line)
        continue
    
    # Another broken block handling just in case
    if "style_block = style_block.replace('" in line and "/* Top Button */" in line:
        skip = True
        continue
        
    out.append(line)

new_text = "".join(out)

# Now Let's ensure extra_css definition is intact and inject the required CSS
css_str = """
/* Top Button */
#topBtn { display: none; position: fixed; bottom: 30px; right: 30px; z-index: 999; font-size: 18px; border: none; outline: none; background-color: var(--red-dark); color: white; cursor: pointer; padding: 15px; border-radius: 50%; box-shadow: 0 4px 12px rgba(0,0,0,0.3); transition: background-color 0.3s; width: 50px; height: 50px; text-align: center; line-height: 20px; }
#topBtn:hover { background-color: var(--red-mid); }
details.plan-details { margin-bottom: 24px; background: var(--g-light); border-radius: 12px; box-shadow: var(--g-shadow); overflow: hidden; }
summary.plan-btn { list-style: none; background: linear-gradient(135deg, var(--red-dark) 0%, #a33030 100%); color: white; padding: 16px 20px; cursor: pointer; font-size: 16px; font-weight: bold; position: relative; user-select: none; transition: background 0.2s; }
summary.plan-btn::-webkit-details-marker { display: none; }
summary.plan-btn::after { content: '+'; position: absolute; right: 20px; top: 50%; transform: translateY(-50%); font-size: 20px; font-weight: bold; }
details[open] summary.plan-btn::after { content: '-'; }
details[open] summary.plan-btn { border-bottom: 3px solid var(--gold); }
.plan-desc { padding: 12px 20px; font-size: 14px; color: #444; background: #fffdfa; border-bottom: 1px solid #eee; }
"""

if "/* Top Button */" not in new_text:
    new_text = new_text.replace('extra_css = """\n', f'extra_css = """\n{css_str}\n')

with open("generate_fukuoka.py", "w", encoding="utf-8") as f:
    f.write(new_text)

print("generate_fukuoka.py Cleaned Up!")
