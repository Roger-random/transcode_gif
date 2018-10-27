#!/usr/bin/python3
from PIL import Image # https://pillow.readthedocs.io

catgif = Image.open("poptartcat.gif")

print()
print("/* Generated from poptartcat.gif */")
print()

# Extract palette (happens to be common to all frames for this GIF)
numcolors = len(catgif.getcolors())

print("const uint32_t cat_palette[{}] = {{".format(numcolors))

palette = catgif.getpalette()

for color in catgif.getcolors():
  print("  0x00{:02X}{:02X}{:02X},".format(*palette[0:3]))
  palette = palette[3:] # This feels very LISP-y

print("};")
print()

frame = 0

try:
  while True:
    scale320 = catgif.resize((320,320),resample=Image.NEAREST)
    crop240 = scale320.crop((0,40,320,280))

    # Scan frame line-by-line, encode pixels via simple run-length encoding

    rlepixels = list()

    currentcolor = None
    currentcount = 0

    for y in range(240):
      for x in range(320):
        pixel = crop240.getpixel((x,y))
        if pixel == currentcolor:
          currentcount = currentcount + 1
        else:
          if currentcount > 0:
            rlepixels.append((currentcolor, currentcount))
          currentcolor = pixel
          currentcount = 1
      # End of line, flush any accumulated pixels.
      if currentcount > 0:
        rlepixels.append((currentcolor, currentcount))
        currentcount = 0

    print("const uint16_t cat_frame{}[{}] = {{".format(frame,len(rlepixels)))

    numperline = 0

    print("  ",end="")
    for encpixel in rlepixels:
      print("0x{:01X}{:03X}, ".format(*encpixel),end="")
      numperline = numperline + 1
      if numperline >= 10:
        print()
        print("  ",end="")
        numperline = 0

    print()
    print("};")
    print()

    frame = frame + 1
    catgif.seek(catgif.tell()+1)

except EOFError:
  pass # No more frames in GIF

print("const uint16_t* cat_frames[{}] = {{".format(frame))

for f in range(frame):
  print("  cat_frame{},".format(f))

print("};")