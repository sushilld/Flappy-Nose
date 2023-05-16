import cv2
import numpy as np
import random
from faceDetect import FaceDetector
import pandas as pd
import os.path as path
import tkinter as tk
import sys
import os
import time


def restart_program():
    python = sys.executable
    os.execl(python, python, * sys.argv)
    

def check_collision_circle_rect(circle_center, circle_radius, rect_points):
    # Check if center of circle is inside rectangle
    if circle_center[0] >= rect_points[0] and circle_center[0] <= rect_points[2] \
       and circle_center[1] >= rect_points[1] and circle_center[1] <= rect_points[3]:
        return True

    # Check if any edge of the rectangle intersects with the circle
    rect_edges = [(rect_points[0], rect_points[1], rect_points[2], rect_points[1]), # Top edge
                  (rect_points[2], rect_points[1], rect_points[2], rect_points[3]), # Right edge
                  (rect_points[2], rect_points[3], rect_points[0], rect_points[3]), # Bottom edge
                  (rect_points[0], rect_points[3], rect_points[0], rect_points[1])] # Left edge

    for edge in rect_edges:
        pt1 = np.array([edge[0], edge[1]])
        pt2 = np.array([edge[2], edge[3]])
        dist = cv2.pointPolygonTest(np.array([pt1, pt2]), circle_center, True)
        if dist >= -circle_radius:
            return True

    return False

__exit = False

def when_clicked():
    __exit == True
    root.destroy()
    
def start_game():
    try:
        df = pd.read_csv('scores.csv')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Name', 'Score'])
    name = name_entry.get()
    cap = cv2.VideoCapture(0)
    frameWidth = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    frameHeight = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    print(frameWidth, frameHeight)

    frame_num = 0

    a1, a2, a3, a4 = 800, 0, 750, int(frameHeight/2)-50
    # rectangles = [(a1, a2, a3, a4)]
    rectangles = []


    b1, b2, b3, b4 = 800, int(frameHeight/2)+50, 750, int(frameHeight)
    # inverse_rectangles = [(b1, b2, b3, b4)]
    inverse_rectangles = []

    detector = FaceDetector()
    collision_num = 0
    collision = False

    Score = 0
    speed = 5
    cv2.setNumThreads(1)

    while True:
        ret, frame = cap.read()
        start_time = time.time()
        frame = cv2.flip(frame, 1)
        frame = detector.findFace(frame, draw=True)
        lmlist = detector.findPosition(frame, draw=False)
        
        if len(lmlist)>0:
            cv2.putText(frame, f'Score: {Score - 2}', (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
            if frame_num % 40 == 0:
                # a1, a2, a3, a4 = a1, a2, a3, a4+random.randint(50,100)
                temp_y = random.randint(int(frameHeight/4),int(frameHeight * 0.75))
                a1, a2, a3, a4 = a1, a2, a3, temp_y-50
                b1, b2, b3, b4 = b1, temp_y+50, b3, b4
                rectangles.append((a1, a2, a3, a4))
                inverse_rectangles.append((b1, b2, b3, b4))
                Score += 1

            if len(rectangles) > 4:
                rectangles = rectangles[1:]
                inverse_rectangles = inverse_rectangles[1:]
            
            # speed = 5
            
            if frame_num % 400 == 0:
                speed += 1
            
            arr = np.array(rectangles)
            arr[:, [0, 2]] -= speed
            rectangles = [tuple(row) for row in arr]
            
            arr = np.array(inverse_rectangles)
            arr[:, [0, 2]] -= speed
            inverse_rectangles = [tuple(row) for row in arr]
            
            for x1, y1, x2, y2 in rectangles:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), -1)
            for x1, y1, x2, y2 in inverse_rectangles:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), -1)

            frame_num += 1   

            # Collision detection between rectangles and landmarks
            
            px, py = int((lmlist[0][1][0] + lmlist[0][1][0] + lmlist[0][1][2]) / 2), int((lmlist[0][1][1] + lmlist[0][1][1] + lmlist[0][1][3]) / 2) 
            point = (px, py)
            frame = cv2.circle(frame, point, 10, (255,0,0), -1)
            
            for rect in rectangles:          
                if check_collision_circle_rect(point, 10, rect):
                    collision = True
                    collision_num += 1
                    print("Collision ->", collision_num)

            if collision == False:
                for rect in inverse_rectangles:
                    if check_collision_circle_rect(point, 10, rect):
                        collision = True
                        collision_num += 1
                        print("Collision ->", collision_num)

            if collision == True:
                cap.release()
                break
            end_time = time.time()
            fps = 1/(end_time - start_time)
            end_time = time.time()
            cv2.putText(frame, f'FPS: {int(fps)}', (10, 100), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
            cv2.namedWindow('frame', cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty('frame', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q') or collision == True:
                root.destroy()
                break
            

    # Release the VideoCapture object and destroy all windows
    cap.release()
    cv2.destroyAllWindows()
    img = np.zeros((int(frameHeight), int(frameWidth),3), dtype=np.uint8)
    img = 255*img
    img_text = cv2.putText(img, "Game Over", (0, int(frameHeight/2)), cv2.FONT_HERSHEY_SIMPLEX, 3, (255,255,255), 2)
    img_text = cv2.putText(img, f"Score: {Score -2 }", (0, int(frameHeight/2)+200), cv2.FONT_HERSHEY_SIMPLEX, 4, (255,255,255), 2)
    # scoreDF.append({'Name': 'Sushil', 'Score': Score - 2}, ignore_index=True)
    # Check if the player is already in the DataFrame
    if name in df['Name'].values:
        # Update the score for the existing player
        df.loc[df['Name'] == name, 'Score'] = Score - 2
    else:    
        new_data = pd.DataFrame({'Name': name, 'Score': Score - 2}, index=[0])
        df = pd.concat([df, new_data], ignore_index=True)

    df.to_csv('scores.csv', index=False)

    cv2.imshow('Warning', img_text)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    root.destroy()
    
    if __exit == False:
        restart_program()


# Read the player names and scores from the CSV file
df = pd.read_csv('scores.csv')
# Sort the dataframe by score in descending order to find the highest score

df_sorted = df.sort_values(by=['Score'], ascending=False).head(5).reset_index()
print(df_sorted)
highest_name = df_sorted.iloc[0]['Name']
highest_score = df_sorted.iloc[0]['Score']
# Create the main window
root = tk.Tk()
root.title('Nose Job')

# Set the size of the window
root.geometry('680x540')

# Add a label for the title
title_label = tk.Label(root, text='Nose Job', font=('Arial', 24))
title_label.pack(pady=10)

# Create a frame for the table
table_frame = tk.Frame(root)
table_frame.pack()

# Add a label for the table header
name_label = tk.Label(table_frame, text='Name', font=('Arial', 16))
name_label.grid(row=0, column=0, padx=10, pady=5)
score_label = tk.Label(table_frame, text='Score', font=('Arial', 16))
score_label.grid(row=0, column=1, padx=10, pady=5)

# Add a row for each player in the table
for i, row in df_sorted.iterrows():
    name = row['Name']
    score = row['Score']
    print(name, score, i)
    name_label = tk.Label(table_frame, text=name, font=('Arial', 14))
    name_label.grid(row=i+1, column=0, padx=10, pady=5)
    score_label = tk.Label(table_frame, text=score, font=('Arial', 14))
    score_label.grid(row=i+1, column=1, padx=10, pady=5)

# Add a label for the highest score
highest_label = tk.Label(root, text='Highest Score: {} - {}'.format(highest_name, highest_score), font=('Arial', 16))
highest_label.pack(pady=10)

# Add a button to start the game
# selected_name = None
# def select_name(name):
#     global selected_name
#     selected_name = name

start_button = tk.Button(root, text='Start Game', command=start_game, font=('Arial', 18))
start_button.pack(pady=20)

# Add a label for the name entry
name_label = tk.Label(root, text='Enter your name:')
name_label.pack()

# Add an entry field for the name
name_entry = tk.Entry(root)
name_entry.pack()

# Exit button
name_label = tk.Button(root, text='Exit Game', command=when_clicked, font=('Arial', 18))
name_label.pack()

# Start the GUI main loop
root.mainloop()