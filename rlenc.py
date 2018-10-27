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
print()

# Scan frame line-by-line, encode pixels via simple run-length encoding

rlepixels = list()

currentcolor = None
currentcount = 0

for y in range(240):
  for x in range(320):
    pixel = crop240.getpixel((x,y))
    if pixel == currentcolor:
      currentcount = currentcount + 1
      if currentcount == 255:
        rlepixels.append((currentcolor, currentcount))
        currentcount = 0
    else:
      if currentcount > 0:
        rlepixels.append((currentcolor, currentcount))
      currentcolor = pixel
      currentcount = 1
  # End of line, flush any accumulated pixels.
  if currentcount > 0:
    rlepixels.append((currentcolor, currentcount))
    currentcount = 0

print("const uint16_t frame{}[{}] = {{".format(frame,len(rlepixels)))

numperline = 0

print("  ",end="")
for encpixel in rlepixels:
  print("0x{:02X}{:02X}, ".format(*encpixel),end="")
  numperline = numperline + 1
  if numperline >= 10:
    print()
    print("  ",end="")
    numperline = 0

print()
print("};")
