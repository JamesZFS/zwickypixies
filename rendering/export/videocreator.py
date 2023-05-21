import cv2
import sys

if __name__ == "__main__":
    frames = sys.argv[1:]
    frame = cv2.imread(frames[0])
    height, width, layers = frame.shape

    video = cv2.VideoWriter("video.avi", 0, 1, (width, height))

    for frame in frames:
        video.write(cv2.imread(frame))

    cv2.destroyAllWindows()
    video.release()