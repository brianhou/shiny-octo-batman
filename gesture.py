import cv2
import numpy as np

PALM_CONCAVITY_DIST_THRESH = 8000


class GestureRecognition:
  def recognize(self):
    cap = cv2.VideoCapture(0)
    old_pos = []
    new_pos = []
    while cap.isOpened():
      ret, img = cap.read()
      imageYCrCb = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)
      min_YCrCb = np.array([0, 133, 77], np.uint8)
      max_YCrCb = np.array([255, 173, 127], np.uint8)
      skinRegion = cv2.inRange(imageYCrCb, min_YCrCb, max_YCrCb)
  
      contours, _ = cv2.findContours(skinRegion, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
      if not contours:
        continue
      cnt = max(contours, key=lambda contour: cv2.contourArea(contour))
      hull = cv2.convexHull(cnt)
      moments = cv2.moments(cnt)
      if moments['m00'] != 0:
        cx = int(moments['m10'] / moments['m00'])
        cy = int(moments['m01'] / moments['m00'])
      else:
        continue
      center = (cx, cy)
      cv2.circle(img, center, 5, [0, 0, 255], 2)

      if len(old_pos) < 5:
        old_pos.append((cx, cy))
      elif len(new_pos) < 5:
        new_pos.append((cx, cy))
      else:
        diff_x = sum([x[0] for x in new_pos]) / len(new_pos) - sum([x[0] for x in old_pos]) / len(old_pos)
        diff_y = sum([x[1] for x in new_pos]) / len(new_pos) - sum([x[1] for x in old_pos]) / len(old_pos)
        if diff_x < -50:
          print "left"
        if diff_x > 50:
          print "right"
        if diff_y < -50:
          print "up"
        if diff_y > 50:
          print "down"
        old_pos.pop(0)
        old_pos.append(new_pos.pop(0))
        new_pos.append((cx, cy))

      cnt = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
      hull = cv2.convexHull(cnt, returnPoints=False)
      defects = cv2.convexityDefects(cnt, hull)
      if defects is None:
        continue
      for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        start = tuple(cnt[s][0])
        end = tuple(cnt[e][0])
        far = tuple(cnt[f][0])
        if (far[0] - cx) ** 2 + (far[1] - cy) ** 2 < PALM_CONCAVITY_DIST_THRESH:
          cv2.line(img, start, end, [0, 255, 0], 2)
          cv2.circle(img, far, 5, [0, 0, 255], -1)

      cv2.imshow('input', img)
      cv2.waitKey(3)


if __name__ == "__main__":
  gr = GestureRecognition()
  gr.recognize()
