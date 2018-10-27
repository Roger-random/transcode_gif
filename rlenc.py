#!/usr/bin/python3
from PIL import Image # https://pillow.readthedocs.io

catgif = Image.open("poptartcat.gif")

frame = 0

scale320 = catgif.resize((320,320),resample=Image.NEAREST)
crop240 = scale320.crop((0,40,320,280))

# Extract palette for this frame

numcolors = len(crop240.getcolors())

print("const uint32_t palette{}[{}] = {{".format(frame,numcolors))

palette = crop240.getpalette()

for color in crop240.getcolors():
  print("  0x00{:02X}{:02X}{:02X},".format(*palette[0:3]))
  palette = palette[3:] # This feels very LISP-y

print("};")
