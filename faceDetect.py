import cv2
import mediapipe as mp
import time
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils


class FaceDetector:
    def __init__(self, min_detection_confidence=0.5, model_selection=0):
        self.min_detection_confidence = min_detection_confidence
        self.model_selection = model_selection
        
        self.mpFace = mp.solutions.face_detection
        self.face = self.mpFace.FaceDetection(self.min_detection_confidence, self.model_selection)
        self.mpDraw = mp.solutions.drawing_utils
    
    def findFace(self, frame, draw = True):
        
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.result = self.face.process(imgRGB)
        
        if self.result.detections:
            for id, detection in enumerate(self.result.detections):
                # mpDraw.draw_detection(frame, detection)
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, ic = frame.shape
                bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                # cv2.rectangle(frame, bbox, (255, 0, 255), 2)
                # cv2.putText(frame, f'{int(detection.score[0]*100)}%', (bbox[0], bbox[1]-20), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
                if draw:
                    self.mpDraw.draw_detection(frame, detection)
        return frame

    def findPosition(self, frame, draw = True):
        lmList = []
        if self.result.detections:
            for id, detection in enumerate(self.result.detections):
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, ic = frame.shape
                bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                lmList.append([id, bbox, detection.score])
                if draw:
                    self.mpDraw.draw_detection(frame, detection)
        return lmList
    
    
    
# if __name__ == "__main__":
#     cap = cv2.VideoCapture(0)
#     new_frame = 0
#     prev_frame = 0
#     detector = FaceDetector()
#     while True:
#         success, img = cap.read()
#         new_frame = time.time()
#         img = detector.findFace(img)
#         # print(detector.findPosition(img, draw=False))
#         fps = 1/(new_frame-prev_frame)
#         prev_frame = new_frame
#         img = cv2.putText(img, f'FPS: {int(fps)}', (20,70), cv2.FONT_HERSHEY_PLAIN, 3, (0,255,0), 3)
#         cv2.imshow("Image", img)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break