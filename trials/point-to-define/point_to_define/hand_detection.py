import cv2
import numpy as np

class HandDetection:
    def __init__(self):
        self.trained_hand = False
        self.hand_row_nw = None
        self.hand_row_se = None
        self.hand_col_nw = None
        self.hand_col_se = None
        self.hand_hist = None

    def take_histogram(self, frame):
        """
        Take a histogram that gets color values.
        Choosing these values are very important
        """
        def bad_histogram():
            rows,cols,_ = frame.shape
            row_1, row_2, row_3 = 2*rows/10, 5*rows/10, 8*rows/10
            col_1, col_2, col_3 = 2*cols/10, 5*cols/10, 8*cols/10
            self.hand_row_nw = np.array([row_1, row_1, row_1,
                                         row_2, row_2, row_2,
                                         row_3, row_3, row_3,])
            self.hand_col_nw = np.array([col_1, col_2, col_3,
                                         col_1, col_2, col_3,
                                         col_1, col_2, col_3])

            self.hand_row_se = self.hand_row_nw + 10
            self.hand_col_se = self.hand_col_nw + 10

        def better_histogram():
            rows,cols,_ = frame.shape
            row_1, row_2, row_3 = 3*rows/10, 5*rows/10, 7*rows/10
            col_1, col_2, col_3 = 4*cols/10, 45*cols/100, 5*cols/10
            self.hand_row_nw = np.array([row_1, row_1, row_1,
                                         row_2, row_2, row_2,
                                         row_3, row_3, row_3,])
            self.hand_col_nw = np.array([col_1, col_2, col_3,
                                         col_1, col_2, col_3,
                                         col_1, col_2, col_3])

            self.hand_row_se = self.hand_row_nw + 10
            self.hand_col_se = self.hand_col_nw + 10

        better_histogram()
        # bad_histogram()

        size = self.hand_row_nw.size
        for i in xrange(size):
            cv2.rectangle(frame,
                          (self.hand_col_nw[i], self.hand_row_nw[i]),
                          (self.hand_col_se[i], self.hand_row_se[i]),
                          (0,255,0),
                          1)
        black = np.zeros(frame.shape, dtype=frame.dtype)
        frame_final = np.vstack([black, frame])
        return frame_final


    def train_hand(self, frame):
        self.set_hand_hist(frame)
        self.trained_hand = True


    def set_hand_hist(self, frame):
        #TODO use constants, only do HSV for ROI
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        roi = np.zeros([90,10,3], dtype=hsv.dtype)

        size = self.hand_row_nw.size
        for i in xrange(size):
            roi[i*10:i*10+10,0:10] = hsv[self.hand_row_nw[i]:self.hand_row_nw[i]+10,
                                                             self.hand_col_nw[i]:self.hand_col_nw[i]+10]

        self.hand_hist = cv2.calcHist([roi],[0, 1], None, [180, 256], [0, 180, 0, 256])
        cv2.normalize(self.hand_hist, self.hand_hist, 0, 255, cv2.NORM_MINMAX)
