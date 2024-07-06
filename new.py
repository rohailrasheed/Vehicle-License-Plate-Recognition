import tkinter
from tkinter import *
from PIL import ImageTk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import cv2
import requests
from pprint import pprint
import numpy as np
from time import sleep
import os
import pandas as pd

temp1 = ''
text_variable = ''
num1,num2 = '',''

#------------------------------------------------------------------------------------------------------------------------- Video Recog

def video_capture():
    global temp1
    lis = []
# Capture Video per Frames
    vid = askopenfilename(initialdir="C:/",filetypes =(("Video File", "*.mp4"),("All Files","*.*")),title = "Choose a file.")
    cap= cv2.VideoCapture(vid)
    i=0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == False:
            break
        cv2.imwrite('cap'+str(i)+'.jpg',frame)
        i+=1
        lis.append(i)

    cap.release()
    cv2.destroyAllWindows()

# Recognize Vehicle Plate through Token Number
    regions = ['gb', 'it'] # Change to your country

    with open('cap{}.jpg'.format(10), 'rb') as fp:
        response = requests.post(
            'https://api.platerecognizer.com/v1/plate-reader/',
            data=dict(regions=regions),  # Optional
            files=dict(upload=fp),
            headers={'Authorization': 'Token fc12b8665a6bcaa682eec5b83d9e1dc03d825252'})
    #pprint(response.json())
    data = response.json()


    s=(data['results'][0]['plate'])
    b=str(s).upper()
    print(b)
    messagebox.showinfo('Recognition','Vehicle Registration: {}'.format(b))
    
    temp1 = b
        

#------------------------------------------------------------------------------------------------------------------------- Image Recog

def images():
    global temp1
    img = askopenfilename(initialdir="C:/",filetypes =(("Image File", "*.jpg"),("All Files","*.*")),title = "Choose a file.")
    regions = ['gb', 'it'] # Change to your country

    with open(img, 'rb') as fp:
        response = requests.post(
            'https://api.platerecognizer.com/v1/plate-reader/',
            data=dict(regions=regions),  # Optional
            files=dict(upload=fp),
            headers={'Authorization': 'Token fc12b8665a6bcaa682eec5b83d9e1dc03d825252'})
    #pprint(response.json())
    data = response.json()


    s=(data['results'][0]['plate'])
    b=str(s).upper()
    print(b)
    messagebox.showinfo('Recognition','Vehicle Registration: {}'.format(b))
    
    temp1 = b
    
#------------------------------------------------------------------------------------------------------------------------- Vehi Count
        
def vehicle_count():
    global text_variable
    text_variable = StringVar()
    
    width_min=80 #Largura minima do retangulo
    height_min=80 #Altura minima do retangulo

    offset=6 #Erro permitido entre pixel  

    pos_line=550 #Posição da linha de contagem 

    delay= 60 #FPS do vídeo

    detect = []
    cars= 0

            
    def catch_center(x, y, w, h):
        x1 = int(w / 2)
        y1 = int(h / 2)
        cx = x + x1
        cy = y + y1
        return cx,cy

    video = askopenfilename(initialdir="C:/",filetypes =(("Video File", "*.mp4"),("All Files","*.*")),title = "Choose a file.")
    cap = cv2.VideoCapture(video)
    subtracao = cv2.bgsegm.createBackgroundSubtractorMOG()

    while True:
        ret , frame1 = cap.read()
        tempo = float(1/delay)
        sleep(tempo) 
        grey = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(grey,(3,3),5)
        img_sub = subtracao.apply(blur)
        dilat = cv2.dilate(img_sub,np.ones((5,5)))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        dilated = cv2.morphologyEx (dilat, cv2. MORPH_CLOSE , kernel)
        dilated = cv2.morphologyEx (dilated, cv2. MORPH_CLOSE , kernel)
        contour,h=cv2.findContours(dilated,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        
        cv2.line(frame1, (25, pos_line), (1200, pos_line), (255,127,0), 3) 
        for(i,c) in enumerate(contour):
            (x,y,w,h) = cv2.boundingRect(c)
            validate_contour = (w >= width_min) and (h >= height_min)
            if not validate_contour:
                continue

            cv2.rectangle(frame1,(x,y),(x+w,y+h),(0,255,0),2)        
            center = catch_center(x, y, w, h)
            detect.append(center)
            cv2.circle(frame1, center, 4, (0, 0,255), -1)

            for (x,y) in detect:
                if y<(pos_line+offset) and y>(pos_line-offset):
                    cars+=1
                    cv2.line(frame1, (25, pos_line), (1200, pos_line), (0,127,255), 3)  
                    detect.remove((x,y))
                    print("car is detected : "+str(cars))
                    text_variable.set(str(cars))
                    

           
        cv2.putText(frame1, "VEHICLE COUNT : "+str(cars), (450, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255),5)
        cv2.imshow("Video Original" , frame1)
        cv2.imshow("Detect",dilated)

        if cv2.waitKey(1) == 27:
            break

    cv2.destroyAllWindows()
    cap.release()



    main = Tk()
    main.geometry('200x100')
    main.title('Counter')

    e1 = Entry(main, bd=4, textvariable=text_variable)
    e1.place(x=10, y=10)


    main.mainloop()

#------------------------------------------------------------------------------------------------------------------------- Load Rec

def check():
    global temp1, num1, num2
    
    df = pd.read_excel('TestData.xlsx')
    
    for i in df['Liscence Number']:
        if str(i) == str(temp1):
            ind = df.index[df['Liscence Number']==temp1].tolist()
            print('Registration:\t', df['Liscence Number'][ind])
            print('Car Name:\t', df['Car'][ind])
            print('Car Model:\t', df['Model'][ind])
            print('Reg. City:\t', df['City'][ind])
            print('Reg. Country:\t', df['Country'][ind])
            print('Challan:\t', df['Challan'][ind])
            print('Issue:\t', df['Issue'][ind])

            num1 = df['Challan'][ind]
            num2 = df['Issue'][ind]
            break

        else:
            print('no challan found')
            break

#-------------------------------------------------------------------------------------------------------------------------
##def message():
##    import smtplib
##    from email.message import EmailMessage
##
##    global temp1, num1, num2
##
##    def email_alert(subject,body,to):
##        global temp1
##        msg = EmailMessage()
##        msg.set_content(body)
##        msg['subject'] = subject
##        msg['to'] = to
##
##        user = "rohailr3@gmail.com"
##        msg['from'] = user
##        password = "pgjeyjmgxjtzcvzk"
##
##        server = smtplib.SMTP("smtp.gmail.com", 587)
##
##        server.starttls()
##
##        server.login(user, password)
##        server.send_message(msg)
##
##        server.quit()
##
##    email_alert("Alert","The car registration number is {} \n\n Challan Status: {} \n\n Challan Issue: {}".format(temp1, str(num1), str(num2)),"aarish22n1@gmail.com")

        
#------------------------------------------------------------------------------------------------------------------------- GUI

gui = Tk()
gui.geometry('840x557')
gui.title('Vehicle Dashboard')

canvas = Canvas(width=600, height=800, bg='black')
canvas.pack(expand=YES, fill=BOTH)

image = ImageTk.PhotoImage(file="back.png")
canvas.create_image(10, 10, image=image, anchor=NW)

canvas.create_text(285,50, text="Vehicle and Liscence Plate Detection", font=('Times New Roman', '25', 'bold'), fill="white")
canvas.pack(fill=BOTH, expand=1)


b1 = Button(text='Detect Liscence Plate with Image', font=('Times New Roman',18,'bold'), bd=8, bg='#278FB4', command=images).place(x=130, y=150)
b2 = Button(text='Detect Liscence Plate with Video', font=('Times New Roman',18,'bold'), bd=8, bg='#278FB4', command=video_capture).place(x=130, y=250)
b3 = Button(text='Detect Vehicle and Road Counting', font=('Times New Roman',17,'bold'), bd=8, bg='#278FB4', command=vehicle_count).place(x=125, y=350)
b2 = Button(text='Check Defaulters through Database', font=('Times New Roman',17,'bold'), bd=8, bg='#278FB4', command=lambda:[check()]).place(x=119, y=450)

mainloop()

#-------------------------------------------------------------------------------------------------------------------------
        
