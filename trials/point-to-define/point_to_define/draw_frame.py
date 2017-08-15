import cv2
import numpy as np
import image_analysis

class DrawFrame:
    def __init__(self):
        self.row_ratio = None
        self.col_ratio = None
        self.text = ''


    def resize(self, frame):
        rows,cols,_ = frame.shape

        ratio = float(cols)/float(rows)
        new_rows = 400
        new_cols = int(ratio*new_rows)

        self.row_ratio = float(rows)/float(new_rows)
        self.col_ratio = float(cols)/float(new_cols)

        resized = cv2.resize(frame, (new_cols, new_rows))
        return resized


    def flip(self, frame):
        flipped = cv2.flip(frame, 1)
        return flipped


    def draw_final(self, frame, hand_detection):
        hand_masked = image_analysis.apply_hist_mask(frame, hand_detection.hand_hist)

        contours = image_analysis.contours(hand_masked)
        if contours is not None and len(contours) > 0:
            max_contour = image_analysis.max_contour(contours)
            hull = image_analysis.hull(max_contour)
            centroid = image_analysis.centroid(max_contour)
            defects = image_analysis.defects(max_contour)

            if centroid is not None and defects is not None and len(defects) > 0:
                farthest_point = image_analysis.farthest_point(defects, max_contour, centroid)

                if farthest_point is not None:
                    self.plot_farthest_point(frame, farthest_point)
                    self.plot_hull(frame, hull)

        # self.plot_text(paper_hand, self.text)
        frame_final = np.vstack([frame])
        return frame_final


    def original_point(self, point):
        x,y = point
        xo = int(x*self.col_ratio)
        yo = int(y*self.row_ratio)
        return (xo,yo)


    def new_point(self, point):
        (x,y) = point
        xn = int(x/self.col_ratio)
        yn = int(y/self.row_ratio)
        return (xn,yn)


    def plot_defects(self, frame, defects, contour):
        if len(defects) > 0:
            for i in xrange(defects.shape[0]):
                s,e,f,d = defects[i,0]
                start = tuple(contour[s][0])
                end = tuple(contour[e][0])
                far = tuple(contour[f][0])
                cv2.circle(frame, start, 5, [255,0,255], -1)


    def plot_farthest_point(self, frame, point):
        cv2.circle(frame, point, 5, [0,0,255], -1)


    def plot_centroid(self, frame, point):
        cv2.circle(frame, point, 5, [255,0,0], -1)


    def plot_hull(self, frame, hull):
        cv2.drawContours(frame, [hull], 0, (255, 0, 0), 2)


    def plot_contours(self, frame, contours):
        cv2.drawContours(frame, contours, -1, (0,255,0), 3)