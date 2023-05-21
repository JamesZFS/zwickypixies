import cv2
import sys
import config
import datetime;


if __name__ == "__main__":
    frames = sys.argv[1:]
    frame = cv2.imread(frames[0])
    height, width, layers = frame.shape
    timestamp = str(datetime.datetime.fromtimestamp(datetime.datetime.now()
                                                    .timestamp())).split(".")[0].replace(":","_").replace( " ", "_")
    video = cv2.VideoWriter("{}_{}.avi".format(config.ArrayName, timestamp), 0, 24, (width, height))
    for frame in frames:
        video.write(cv2.imread(frame))
    cv2.destroyAllWindows()
    video.release()