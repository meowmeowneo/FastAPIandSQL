from fastapi import FastAPI, UploadFile, File
import shutil
import cv2
import mediapipe as mp
import base64
import uvicorn

app = FastAPI()
file = "meow.mp4"
out_vid_path = "reloadedmeow.mp4"
out_photo_path = "photomeoq.jpeg"

def hand_rec_video(file, out_vid_path, out_photo_path):
    res = []
    k = 0
    try:
        video = cv2.VideoCapture(file)
        hand = mp.solutions.hands.Hands(static_image_mode=False,
                                        max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
        mpDraw = mp.solutions.drawing_utils

        colorgreen = [0, 200, 0]
        colorred = [0, 0, 255]
        radius = 10
        index_open = False
        middle_open = False
        pinky_open = False
        ring_open = False
        thumb_open = False

        # Используем mp4v для кодирования в mp4
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = None

        while True:
            ret, image = video.read()
            if not ret:
                break

            if out is None:
                h, w, _ = image.shape
                # Указываем размер кадра как (ширина, высота) и fps
                out = cv2.VideoWriter(out_vid_path, fourcc, 20.0, (w, h))

            results = hand.process(image)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mpDraw.draw_landmarks(image, results.multi_hand_landmarks[0], mp.solutions.hands.HAND_CONNECTIONS,
                                          landmark_drawing_spec=mpDraw.DrawingSpec(color=(0, 0, 255)))
                    for lm in hand_landmarks.landmark:
                        a1, b2 = int(lm.x * w), int(lm.y * h)
                        coordinates = (a1, b2)
                        cv2.circle(image, coordinates, radius, colorred)

                        index_coord6y = (
                            int(results.multi_hand_landmarks[0].landmark[6].y * h))
                        index_coord8y = (
                            int(results.multi_hand_landmarks[0].landmark[8].y * h))

                        middle_coord12y = (
                            int(results.multi_hand_landmarks[0].landmark[12].y * h))

                        pinky_coord20y = (
                            int(results.multi_hand_landmarks[0].landmark[20].y * h))

                        ring_coord16y = (
                            int(results.multi_hand_landmarks[0].landmark[16].y * h))

                        if index_coord6y < index_coord8y:
                            index_open = False
                        else:
                            index_open = True
                        if index_coord6y < middle_coord12y:
                            middle_open = False
                        else:
                            middle_open = True
                        if index_coord6y < ring_coord16y:
                            ring_open = False
                        else:
                            ring_open = True
                        if index_coord6y < pinky_coord20y:
                            pinky_open = False
                        else:
                            pinky_open = True

                        if ((index_open is True) and (middle_open is True) and (ring_open is False) and (pinky_open is False)):
                            cv2.circle(image, coordinates, radius,
                                       colorgreen, thickness=1)
                            mpDraw.draw_landmarks(image, results.multi_hand_landmarks[0],
                                                  mp.solutions.hands.HAND_CONNECTIONS,
                                                  landmark_drawing_spec=mpDraw.DrawingSpec(color=(0, 200, 0)))
                            if k == 0:
                                print('Peace!')
                                cv2.imwrite(out_photo_path, image)
                                k += 1
                            res.append('True')

            out.write(image)  # Записываем кадр с отрисованными точками

        out.release()
        video.release()
        cv2.destroyAllWindows()

    except Exception as e:
        return str(f"Error: {e}")
    if 'True' in res:
        return [out_photo_path, out_vid_path]
    else:
        return False

@app.post("/")
async def upload_video(video: UploadFile = File(...)):
    try:
        with open(f"{video.filename}", "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        
        hand_rec_video(file, out_vid_path, out_photo_path)

        with open(out_vid_path, "rb") as video_file:
            video_data = base64.b64encode(video_file.read()).decode('utf-8')

        with open(out_photo_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')

        data = {"video": video_data, "image": image_data}

        return data
    except Exception as e:
        return {"error": f"Произошла ошибка при загрузке файла: {str(e)}"}
    