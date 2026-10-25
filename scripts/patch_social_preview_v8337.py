from pathlib import Path
import shutil,sys
p=Path(sys.argv[1])
shutil.copyfile('assets/share-logo.png',p.parent/'share-logo.png')
a=p.parent/'admin.html';a.write_text(a.read_text().replace('id="adminVersion">V8.336','id="adminVersion">V8.337'))
print('V8.337 editable social sharing image integrated')
