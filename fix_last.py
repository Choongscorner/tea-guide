import re

with open("generate_fukuoka.py", "r", encoding="utf-8") as f:
    text = f.read()

pattern = r"</style>\n\"\"\"\n    style_block = style_block\.replace\('\n  /\* Top Button \*/[\s\S]*?</style>', extra_css\)"
replacement = '"""\n    style_block = style_block.replace("</style>", extra_css + "</style>")'

new_text = re.sub(pattern, replacement, text)

# Just in case there are multiple, apply it.
with open("generate_fukuoka.py", "w", encoding="utf-8") as f:
    f.write(new_text)

print("generate_fukuoka.py fixed correctly!")
