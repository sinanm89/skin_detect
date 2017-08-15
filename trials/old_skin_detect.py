# flake8: noqa
from time import sleep
import numpy as np
import cv2

def draw_contours(orig_frame, skinMask):

    def contours(frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret,thresh = cv2.threshold(gray, 0, 255, 0)
        # ret,thresh = cv2.threshold(gray,127,255,cv2.THRESH_TOZERO)
        # ret,thresh = cv2.threshold(gray,127,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C)
        # ret,thresh = cv2.threshold(gray,127,255,cv2.ADAPTIVE_THRESH_MEAN_C)
        ret,thresh = cv2.threshold(gray,127,255,cv2.AgastFeatureDetector_AGAST_5_8)
        frame, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # cv2.imshow("images5", thresh)
        # cv2.moveWindow("images5", 500,500)
        return contours

    contours = contours(skinMask)

    if contours is not None and len(contours) > 0:
        for i in contours:
            hull = cv2.convexHull(i)
            cv2.drawContours(orig_frame, [hull], 0, (255, 0, 0), 2)
    return orig_frame

def normalized(rgb):
    """
    Normalize the picture given.
    This is so the light hues are more balanced
    and a better sample can be taken from it.

    :param rgb: picture
    :return: normalized picture
    """
    norm=np.zeros((480,270,3),np.float32)
    norm_rgb=np.zeros((480,270,3),np.uint8)


    b=rgb[:,:,0]
    g=rgb[:,:,1]
    r=rgb[:,:,2]

    sum=b+g+r

    norm[:,:,0]=b/sum*255.0
    norm[:,:,1]=g/sum*255.0
    norm[:,:,2]=r/sum*255.0

    norm_rgb=cv2.convertScaleAbs(norm)
    return norm_rgb

def norm2(frame):
    arr = frame.copy()
    for i in range(3):
        minval = arr[..., i].min()
        maxval = arr[..., i].max()

        if minval != maxval:
            arr[..., i] -= minval
            arr[..., i] *= (255.0 / (maxval + minval))
    cv2.imshow('normalized',arr)
    cv2.moveWindow("normalized", frame.shape[1]+50,0)

def norm3(frame):
    arr = frame.copy()
    cv2.normalize()

def start_training(frame):

    # frame = cv2.cvtColor(frame, cv2.CV_8UC3)
    # split_rgb = cv2.split(rgb32f)[0]
    # sum_rgb = split_rgb[0] + split_rgb[1] + split_rgb[2]
    # split_rgb[0].fill(0)
    # split_rgb[1] = split_rgb[1] / sum_rgb
    # split_rgb[2] = split_rgb[2] / sum_rgb
    # cv2.merge(split_rgb,rgb32f)
    # cv2.imshow('imgggggg',rgb32f)

    # norm=np.zeros(frame.shape,np.float32)
    norm=frame.copy()
    r,g,b=cv2.split(frame)

    # norm_rgb=np.zeros(frame.shape,np.uint8)
    # r=frame[...,0] #red
    # g=frame[...,1] #green
    # b=frame[...,2] #blue

    # sum=(((b.max()+b.min())/2)+((g.max()+g.min())/2)+((r.max()+r.min())/2))/300
    sum = b+g+r
    # sum = g+r

    norm[...,0]=r/sum*255
    norm[...,1]=g/sum*255.0
    norm[...,2]=b/sum*255.0

    norm_rgb=cv2.convertScaleAbs(norm)
    # norm_rgb = cv2.merge(norm, frame)
    cv2.imshow('images2',norm_rgb)
    cv2.moveWindow("images2", 0, 0)
    return norm


def resize_to_ratio(frame):
    rows,cols,_ = frame.shape

    ratio = float(cols)/float(rows)
    new_rows = 400
    new_cols = int(ratio*new_rows)

    resized_image = cv2.resize(frame, (new_cols, new_rows))
    return resized_image


def main():
    # define the upper and lower boundaries of the HSV pixel
    # intensities to be considered 'skin'

    # lower = np.array([0, 48, 80], np.uint8)
    lower = np.array([0, 48, 80], np.uint8)
    # upper = np.array([20, 255, 255], np.uint8)

    # lower = np.array([0,30,60],np.uint8)
    upper = np.array([20,150,179],np.uint8) #HSV: V-79%
    # upper = np.array([10,180,179],np.uint8) #HSV: V-79%
    # webcam capture
    camera = cv2.VideoCapture(0)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    iterations = 18
    while True:
        # grab the current frame
        (grabbed, frame) = camera.read()

        # resize the frame, convert it to the HSV color space,
        # and determine the HSV pixel intensities that fall into
        # the speicifed upper and lower boundaries

        frame = resize_to_ratio(frame)
        # frame = cv2.GaussianBlur(frame, (3, 3), 1)
        # cv2.normalize(frame,frame,0,255,cv2.NORM_MINMAX)
        # GET HSV IMAGE
        converted = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # inRange(nrgb, Scalar(0,0.28,0.36), Scalar(1.0,0.363,0.465)
        skinMask = cv2.inRange(converted, lower, upper)

        # aa = normalized(frame)
        # apply a series of erosions and dilations to the mask
        # using an elliptical kernel

        skinMask = cv2.dilate(skinMask, kernel, iterations=2)
        skinMask = cv2.erode(skinMask, kernel, iterations=2)

        # skinMask = cv2.erode(skinMask, kernel, iterations=2)
        # skinMask = cv2.dilate(skinMask, kernel, iterations=2)

        # blur the mask to help remove noise, then apply the
        # mask to the frame
        # skinMask = cv2.GaussianBlur(skinMask, (3, 3), 0)
        skin = cv2.bitwise_and(frame, frame, mask=skinMask)
        # cv2.normalize(skin,skin,0,255,cv2.NORM_MINMAX)

        tv = np.hstack([
            np.vstack([frame, skin]),]
            # np.hstack([skinMask, skinMask])]
                  )
        # cv2.imshow('img',converted)
        # edges = cv2.Canny(skin,100,200)

        cv2.imshow("images", tv)
        # cv2.imshow('img',skinMask)
        # cv2.moveWindow("img", 0, 600)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret,thresh = cv2.threshold(gray, 0, 255, 0)
        frame, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        contour_frame = draw_contours(skin, skin)
        #
        cv2.imshow("images25", contour_frame)
        cv2.moveWindow("images25", 0, 600)
        if iterations > 0:
            mean, std_dev = cv2.meanStdDev(skin, mask=skinMask)
            for i in range(3):
                lower[i] = lower[i] + (std_dev[i]/255)
                upper[i] = upper[i] - (std_dev[i]/255)
            iterations -= 1
        if cv2.waitKey(2) & 0xFF == ord("e"):
            # r,g,b = cv2.split(skin)
            # r_non_zero = cv2.findNonZero(r)
            # g_non_zero = cv2.findNonZero(g)
            # b_non_zero = cv2.findNonZero(b)
            mean, std_dev = cv2.meanStdDev(skin, mask=skinMask)
            for i in range(3):
                lower[i] = lower[i] + (std_dev[i]/255)
                upper[i] = upper[i] - (std_dev[i]/255)
            continue
            # skinMask = cv2.erode(skinMask, kernel, iterations=2)

        if cv2.waitKey(2) & 0xFF == ord("q"):
            break
        else:
            continue
    camera.release()
    cv2.destroyWindow('images')
    # while True:
        # cv2.destroyAllWindows()
        # start_training(frame)
        # cv2.calcHist(frame,)
        # if cv2.waitKey(2) & 0xFF == ord("e"):
        #     break
        # else:
        #     continue
    # cleanup
    # camera.release()
    cv2.destroyAllWindows()


def smth():


    img = cv2.imread('/Users/snn/Documents/projects/Scrunch/skinny/skinny/tests/images/snn.jpg')
    h = np.zeros((300,256,3))                                    # image to draw histogram

    bins = np.arange(256).reshape(256,1)                         # Number of bins, since 256 colors, we need 256 bins
    color = [ (255,0,0),(0,255,0),(0,0,255) ]

    for ch,col in enumerate(color):
        hist_item = cv2.calcHist([img],[ch],None,[256],[0,256])  # Calculates the histogram
        cv2.normalize(hist_item,hist_item,0,255,cv2.NORM_MINMAX) # Normalize the value to fall below 255, to fit in image 'h'

        hist=np.int32(np.around(hist_item))
        pts = np.column_stack((bins,hist))                       # stack bins and hist, ie [[0,h0],[1,h1]....,[255,h255]]
        cv2.polylines(h,[pts],False,col)

    h=np.flipud(h)                                               # You will need to flip the image vertically

    cv2.imshow('colorhist',hist_item)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def mtf(frame):

    cv2.normalize(frame,frame,0,255,cv2.NORM_MINMAX)
    cv2.imshow('colorhist',frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    frame = cv2.imread("/Users/snn/Documents/projects/Scrunch/skinny/skinny/tests/images/snn.jpg")
    # converted = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # frame = resize_to_ratio(frame)
    # cv2.imshow('original', frame)
    # start_training(frame)
    # smth()
    # mtf(frame)
    # norm3(frame)
    main()
    while True:
        if cv2.waitKey(2) & 0xFF == ord("q"):
            break
        else:
            continue
    cv2.destroyAllWindows()
    # main()