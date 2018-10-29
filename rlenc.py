#!/usr/bin/python3
from PIL import Image # https://pillow.readthedocs.io
import math

catgif = Image.open("poptartcat.gif")

print()
print("/* Generated from poptartcat.gif */")
print()

reduction = 4 # 1 = full resolution, 2 = half, 4 = quarter, which is still recognizable, 8 = unusable
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

    # Each run length encode takes 3 bytes, but the final one may spill into
    # an extra byte so we need to round up.
    numbytes = len(rlepixels) + math.ceil(len(rlepixels)/2)

    print("const uint8_t cat{}_frame{}[{}] = {{".format(reduction,frame,numbytes))

    numperline = 0
    remaindernibble = None

    print("  ",end="")
    for encpixel in rlepixels:
      pixelcolor =    encpixel[0] & 0xF
      pixelcountmsb = (encpixel[1]>>4) & 0xF
      pixelcountlsb = encpixel[1] & 0xF
      if remaindernibble is not None:
        print("0x{:02X},".format((remaindernibble<<4) | pixelcolor),end="")
        numperline = numperline + 1
        if numperline >= 15:
          print()
          print("  ",end="")
          numperline = 0
        print("0x{:02X},".format(encpixel[1]),end="")
        remaindernibble = None
        numperline = numperline + 1
      else:
        print("0x{:02X},".format((pixelcolor<<4) | pixelcountmsb),end="")
        remaindernibble = pixelcountlsb
        numperline = numperline + 1
      if numperline >= 15:
        print()
        print("  ",end="")
        numperline = 0
    if remaindernibble is not None:
      print("0x{:02X},".format((remaindernibble<<4)),end="")

    print()
    print("};")
    print()

    frame = frame + 1
    catgif.seek(catgif.tell()+1)

except EOFError:
  pass # No more frames in GIF

print("const uint8_t* cat{}_frames[{}] = {{".format(reduction,frame))

for f in range(frame):
  print("  cat{}_frame{},".format(reduction,f))

print("};")