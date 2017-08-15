import cv2
from draw_frame import DrawFrame
from hand_detection import HandDetection

def loop(output_video):
    camera = cv2.VideoCapture(0)
    record_video = False

    df = DrawFrame()
    hd = HandDetection()

    while True:
        # get frame
        (grabbed, frame_in) = camera.read()

        # shrink frame
        frame = df.resize(frame_in)

        # flipped frame to draw on
        frame_final = df.flip(frame)

        # click h to train hand
        if cv2.waitKey(1) == ord('h') & 0xFF:
            hd.train_hand(frame)
        # click q to quit
        if cv2.waitKey(1) == ord('q') & 0xFF:
            break

        # create frame depending on trained status
        if not hd.trained_hand:
            frame_final = hd.take_histogram(frame_final)
        elif hd.trained_hand:
            frame_final = df.draw_final(frame_final, hd)

        # display frame
        cv2.imshow('image', frame_final)

    # cleanup
    camera.release()
    cv2.destroyAllWindows()
