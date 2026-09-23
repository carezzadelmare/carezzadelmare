from pathlib import Path
p=Path('index.html');s=p.read_text(encoding='utf-8')
tag='<script src="eventi/loader.js"></script>'
if tag not in s:s=s.replace('</body>',tag+'\n</body>')
p.write_text(s,encoding='utf-8')
