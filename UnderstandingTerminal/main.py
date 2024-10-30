import random
import math
import os

SCREEN_SIZE = (60,181)
SCREEN_PIXELS = [ 0 for _ in range(SCREEN_SIZE[0]*SCREEN_SIZE[1]) ]

LUMA_LEVELS = [' ', '.', '░', '▒', '@', 'O', '0' , '▓', '█']

def idx(i,j,size):
    return i*size[1]+j

def clamp(x,xmin,xmax):
    if x < xmin:
        return xmin
    if x > xmax:
        return xmax
    return x

def readPPM(filePath):
    lines = open(filePath,'rb').read()

    state = 0
    header = ''
    widthHeightLine = ''
    maxPixelValue = ''
    image = []
    remainingDataStart = 0

    for i,c in enumerate(lines):
        if state == 0:
            c = chr(c)
            header += c
            if c == '\n':
                header = header.strip()
                if header != 'P6':
                    raise Exception('Bad ppm file')
                state = 1
        elif state == 1:
            c = chr(c)
            widthHeightLine += c
            if c == '\n':
                width,height = widthHeightLine.strip().split()
                width = int(width)
                height = int(height)
                state = 2
                image = [ 0 for _ in range(width*height) ] #Luma image only
        elif state == 2:
            c = chr(c)
            maxPixelValue += c
            if c == '\n':
                maxPixelValue = int(maxPixelValue.strip()) + 1
                state = 3
                remainingDataStart = i+1
                break
    
    assert(state == 3)
    assert(width != 0 and height != 0)
    assert(remainingDataStart != 0)
    lines = lines[remainingDataStart:]
    assert(len(lines) == width*height*3)

    imageIdx = 0
    rgbIdx = 0

    for c in lines:
        image[imageIdx] += int(c)

        if rgbIdx == 2:
            image[imageIdx] /= 3
            image[imageIdx] = image[imageIdx]*len(LUMA_LEVELS)/maxPixelValue
            imageIdx += 1
        rgbIdx = (rgbIdx+1)%3

    return image,(height,width)

def renderScreen(screenSize,screenPixels):
    render = ''
    for i in range(screenSize[0]):
        for j in range(screenSize[1]):
            pixelValue = screenPixels[idx(i,j,screenSize)]
            pixelValue = clamp(int(round(pixelValue)),0,len(LUMA_LEVELS)-1)
            render += LUMA_LEVELS[pixelValue]
        render += '\n'
    os.system('clear')
    print(render[:-1],end='')


def getImageSliceAvg(image,imageSize,sliceStart,sliceEnd):
    s = 0
    c = 0
    for i in range(sliceStart[0],sliceEnd[0]):
        for j in range(sliceStart[1],sliceEnd[1]):
            s+=image[idx(i,j,imageSize)]
            c+=1
    return s/c

def downscaleImage(image,imageSize,target,targetImageSize):

    widthScale = targetImageSize[1]/imageSize[1]
    heightScale = targetImageSize[0]/imageSize[0]

    for i in range(targetImageSize[0]):
        for j in range(targetImageSize[1]):
            wS = round(j/widthScale)
            wE = round((j+1)/widthScale)+1

            hS = round(i/heightScale)
            hE = round((i+1)/heightScale)+1

            wS = clamp(wS,0,imageSize[1]-1)
            wE = clamp(wE,0,imageSize[1])
            hS = clamp(hS,0,imageSize[0]-1)
            hE = clamp(hE,0,imageSize[0])
            
            target[idx(i,j,targetImageSize)] = getImageSliceAvg(image,imageSize,(hS,wS),(hE,wE))

def copyToBuffer(image,imageSize,target,targetSize):
    minEnd = min(imageSize[0],targetSize[0]),min(imageSize[1],targetSize[1])
    for i in range(minEnd[0]):
        for j in range(minEnd[1]):
            target[idx(i,j,targetSize)] = image[idx(i,j,imageSize)]


def computeScreen(screenSize,screenPixels,t):
    t = math.sin(t*.1)*.1
    for i in range(screenSize[0]):
        for j in range(screenSize[1]):
            u = i
            v = j

            u = (u - (screenSize[0]/2))/screenSize[0]
            v = (v - (screenSize[1]/2))/screenSize[0]

            u += t

            v*=.5

            l = u*u + v*v
            l = l**.5            


            l*=10

            l = clamp(l,0,len(LUMA_LEVELS)-1)
            l = int(round(l))

            screenPixels[idx(i,j,screenSize)] = l

image,imageSize = readPPM('./sampleImage.ppm')
downscaleImage(image,imageSize,SCREEN_PIXELS,SCREEN_SIZE)
#copyToBuffer(image,imageSize,SCREEN_PIXELS,SCREEN_SIZE)

t=0
while True:
    #computeScreen(SCREEN_SIZE,SCREEN_PIXELS,t)
    renderScreen(SCREEN_SIZE,SCREEN_PIXELS)
    t+=1

