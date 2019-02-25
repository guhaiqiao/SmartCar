############################
#  此模块包含视觉定位的相关类
############################
import numpy as np
import cv2 as cv
import threading


class VisionPositioning:
    def __init__(self):
        self.track_flag = False
        self.x = 0
        self.y = 0

    def track(self):
        cap = cv.VideoCapture(0)

        # set up the ROI for tracking
        roi = cv.imread('car.jpg')
        hsv_roi =  cv.cvtColor(roi, cv.COLOR_BGR2HSV)
        mask = cv.inRange(hsv_roi, np.array((0., 60.,32.)), np.array((180.,255.,255.)))
        roi_hist = cv.calcHist([hsv_roi], [0, 1], mask, [180, 256], [0, 180, 0, 256])
        cv.normalize(roi_hist,roi_hist,0,255,cv.NORM_MINMAX)

        # setup initial location of window
        r,h,c,w = 590,100,172,200  # simply hardcoded the values
        track_window = (c,r,w,h)

        # Setup the termination criteria, either 10 iteration or move by atleast 1 pt
        term_crit = ( cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 1 )

        while self.track_flag:
            ret, frame = cap.read()
            if ret:
                hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
                dst = cv.calcBackProject([hsv],[0,1],roi_hist,[0,180,0,256],1)
                # Now convolute with circular disc
                disc = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))
                cv.filter2D(dst, -1, disc, dst)

                # apply meanshift to get the new location
                ret, track_window = cv.CamShift(dst, track_window, term_crit)

                # Draw it on image
                pts = cv.boxPoints(ret)
                pts = np.int0(pts)
                self.x = (pts[0][0] + pts[1][0]) // 2 + (pts[2][0] - pts[1][0]) // 2
                self.y = (pts[0][1] + pts[1][1]) // 2 + (pts[2][1] - pts[1][1]) // 2
        cap.release()

    def begin_track(self):
        self.track_flag = True
        self.track_thread = threading.Thread(target=self.track, daemon=True)
        self.track_thread.start()

    def stop_track(self):
        self.track_flag = False
        if threading.current_thread() != self.track_thread:
            self.track_thread.join()
            self.track_thread = None

    def get_position(self):
        return self.x, self.y

if __name__ == '__main__':
    cap = cv.VideoCapture('test_positioning.mp4')
    # fourcc = cv.VideoWriter_fourcc(*'XVID')
    # out = cv.VideoWriter('output.mp4',fourcc, 30.0, (544,960))

    # set up the ROI for tracking
    roi = cv.imread('car.jpg')
    hsv_roi = cv.cvtColor(roi, cv.COLOR_BGR2HSV)
    mask = cv.inRange(hsv_roi, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
    roi_hist = cv.calcHist([hsv_roi], [0, 1], mask, [180, 256], [0, 180, 0, 256])
    cv.normalize(roi_hist, roi_hist, 0, 255, cv.NORM_MINMAX)

    # setup initial location of window
    r, h, c, w = 590, 100, 172, 200  # simply hardcoded the values
    track_window = (c, r, w, h)

    # Setup the termination criteria, either 10 iteration or move by atleast 1 pt
    term_crit = (cv.TERM_CRITERIA_EPS | cv.TERM_CRITERIA_COUNT, 10, 1)

    while True:
        ret, frame = cap.read()
        if ret:
            hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
            dst = cv.calcBackProject([hsv], [0, 1], roi_hist, [0, 180, 0, 256], 1)
            # Now convolute with circular disc
            disc = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))
            cv.filter2D(dst, -1, disc, dst)

            # apply meanshift to get the new location
            ret, track_window = cv.CamShift(dst, track_window, term_crit)

            # Draw it on image
            pts = cv.boxPoints(ret)
            pts = np.int0(pts)
            center_x = (pts[0][0] + pts[1][0]) // 2 + (pts[2][0] - pts[1][0]) // 2
            center_y = (pts[0][1] + pts[1][1]) // 2 + (pts[2][1] - pts[1][1]) // 2
            img2 = cv.polylines(frame, [pts], True, 255, 2)
            img2 = cv.circle(img2, (center_x, center_y), 10, (0, 0, 255))
            # out.write(img2)
            cv.imshow('img2', img2)
            cv.imshow('backpro', dst)
            k = cv.waitKey(60) & 0xff
            if k == 27:
                break
        else:
            break
    cv.destroyAllWindows()
    cap.release()
    # out.release()