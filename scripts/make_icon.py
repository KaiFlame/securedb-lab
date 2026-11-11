from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
image=Image.new('RGBA',(256,256),'#fcfbf9')
draw=ImageDraw.Draw(image)
for bounds,color in [((46,78,87,196),'#7f2626'),((104,42,145,214),'#b43f32'),((162,94,203,174),'#db6a35')]:
    draw.rounded_rectangle(bounds,radius=3,fill=color)
target=ROOT/'assets/securedb.ico';target.parent.mkdir(exist_ok=True)
image.save(target,format='ICO',sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
print('Ícone do atalho gerado.')
