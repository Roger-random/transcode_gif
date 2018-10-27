#!/usr/bin/python3
from PIL import Image # https://pillow.readthedocs.io

catgif = Image.open("poptartcat.gif")

print()
print("/* Generated from poptartcat.gif */")
print()

reduction = 1 # 1 = full resolution, 2 = half, 4 = quarter, which looks pretty bad.
screenwidth = 320
screenheight= 240

# Extract palette (happens to be common to all frames for this GIF)
numcolors = len(catgif.getcolors())

print("const uint32_t cat{}_palette[{}] = {{".format(reduction,numcolors))

palette = catgif.getpalette()

for color in catgif.getcolors():
  print("  0x00{:02X}{:02X}{:02X},".format(*palette[0:3]))
  palette = palette[3:] # This feels very LISP-y

print("};")
print()

frame = 0

try:
  while True:
    scaled = catgif.resize((int(screenwidth/reduction),int(screenwidth/reduction)),resample=Image.NEAREST)
    cropoffsety = int((screenwidth-screenheight)/(2*reduction))
    cropped = scaled.crop((0,cropoffsety,int(screenwidth/reduction),int(screenheight/reduction)+cropoffsety))

    # Scan frame line-by-line, encode pixels via simple run-length encoding

    rlepixels = list()

    currentcolor = None
    currentcount = 0

    for y in range(int(240/reduction)):
      for x in range(int(320/reduction)):
        pixel = cropped.getpixel((x,y))
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

    print("const uint16_t cat{}_frame{}[{}] = {{".format(reduction,frame,len(rlepixels)))

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

print("const uint16_t* cat{}_frames[{}] = {{".format(reduction,frame))

for f in range(frame):
  print("  cat{}_frame{},".format(reduction,f))

print("};")