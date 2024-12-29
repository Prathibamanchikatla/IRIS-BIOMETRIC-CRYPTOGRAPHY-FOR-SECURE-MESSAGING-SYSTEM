from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
import os
import pymysql
from django.core.files.storage import FileSystemStorage
from cryptosteganography import CryptoSteganography
from Daugman import find_iris ,daugman
import cv2
from datetime import date
import pyaes, pbkdf2, binascii, secrets
import base64
from hashlib import sha256
import numpy as np
global username
crypto_steganography = CryptoSteganography('securehiding')
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import numpy as np
from inference_sdk import InferenceHTTPClient
import supervision as sv

@csrf_exempt
def search_receiver(request):
    if request.method == 'POST':
        query = json.loads(request.body).get('query', '')
        con = pymysql.connect(host='localhost', port=3306, user='pavithra', password='123456789', database='irisauth', charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("SELECT username, name FROM receivers WHERE name LIKE %s", ('%' + query + '%',))
            rows = cur.fetchall()
            receivers = [{'username': row[0], 'name': row[1]} for row in rows]
        return JsonResponse({'receivers': receivers})
    return JsonResponse({'receivers': []})



def getKey(): #generating key with PBKDF2 for AES
    password = "s3cr3t*c0d3"
    passwordSalt = '76895'
    key = pbkdf2.PBKDF2(password, passwordSalt).read(32)
    return key

def encrypt(plaintext): #AES data encryption
    aes = pyaes.AESModeOfOperationCTR(getKey(), pyaes.Counter(31129547035000047302952433967654195398124239844566322884172163637846056248223))
    ciphertext = aes.encrypt(plaintext)
    return ciphertext

def decrypt(enc): #AES data decryption
    aes = pyaes.AESModeOfOperationCTR(getKey(), pyaes.Counter(31129547035000047302952433967654195398124239844566322884172163637846056248223))
    decrypted = aes.decrypt(enc)
    return decrypted 

def ViewMessage(request):
    if request.method == 'GET':
        global username
        font = '<font size="" color="black">'
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Message ID</font></th>'
        output+='<th><font size=3 color=black>Sender Name</font></th>'
        output+='<th><font size=3 color=black>Receiver Name</font></th>'
        output+='<th><font size=3 color=black>Encrypted Message</font></th>'
        output+='<th><font size=3 color=black>Decrypted Message</font></th>'
        output+='<th><font size=3 color=black>Message Date/font></th></tr>'
        con = pymysql.connect(host='localhost',port = 3306,user = 'root', password = '123456789', database = 'irisauth',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM messages where receiver='"+username+"' or sender='"+username+"'")
            rows = cur.fetchall()
            for row in rows:
                enc = row[3]
                enc = base64.b64decode(enc)
                decrypted = decrypt(enc)
                decrypted = decrypted.decode("utf-8")
                output += "<tr><td>"+font+str(row[0])+"</td>"
                output += "<td>"+font+row[1]+"</td>"
                output += "<td>"+font+row[2]+"</td>"
                output += "<td>"+font+row[3]+"</td>"
                output += "<td>"+font+decrypted+"</td>"
                output += "<td>"+font+row[4]+"</td></tr>" 
        output+="<br/><br/><br/><br/><br/><br/>"
        context= {'data': output} 
        return render(request, 'UserScreen.html', context) 
                


# def PostMessage(request):
#     if request.method == 'GET':
#         global username
#         output = '<select name="t1">'
#         con = pymysql.connect(host='localhost',port = 3306,user = 'root', password = '123456789', database = 'irisauth',charset='utf8')
#         with con:
#             cur = con.cursor()
#             cur.execute("select username FROM register")
#             rows = cur.fetchall()
#             for row in rows:
#                 if row[0] != username:
#                     output += '<option value="'+row[0]+'">'+row[0]+'</option>'
#         context= {'receivers': output}            
#         return render(request, 'PostMessage.html', context)

# def PostMessageAction(request):
#     global username
#     if request.method == 'POST':
#         receiver = request.POST.get('t1', False)
#         msg = request.POST.get('t2', False)
#         today = str(date.today())
#         msg = encrypt(msg)
#         msg = str(base64.b64encode(msg),'utf-8')
#         msg_id = 0
#         con = pymysql.connect(host='localhost',port = 3306,user = 'root', password = '123456789', database = 'irisauth',charset='utf8')
#         with con:
#             cur = con.cursor()
#             cur.execute("select max(msg_id) FROM messages")
#             rows = cur.fetchall()
#             for row in rows:
#                 msg_id = row[0]
#         if msg_id is not None:
#             msg_id = msg_id + 1
#         else:
#             msg_id = 1
#         db_connection = pymysql.connect(host='localhost',port = 3306,user = 'root', password = '123456789', database = 'irisauth',charset='utf8')
#         db_cursor = db_connection.cursor()
#         student_sql_query = "INSERT INTO messages(msg_id,sender,receiver,message,msg_date) VALUES('"+str(msg_id)+"','"+username+"','"+receiver+"','"+msg+"','"+today+"')"
#         db_cursor.execute(student_sql_query)
#         db_connection.commit()
#         output = "Encrypted Msg = "+msg+"<br/>"
#         output += "Message ID = "+str(msg_id)+"<br/>"
#         output += "Message Sent to Receiver : "+receiver+"<br/>"
#         context= {'data':output}
#         return render(request, 'PostMessage.html', context)
# import json

# def PostMessage(request):
#     if request.method == 'GET':
#         global username
#         con = pymysql.connect(host='localhost', port=3306, user='root', password='123456789', database='irisauth', charset='utf8')
#         receivers = []
#         with con:
#             cur = con.cursor()
#             cur.execute("select username FROM register")
#             rows = cur.fetchall()
#             for row in rows:
#                 if row[0] != username:
#                     receivers.append(row[0])
#         context = {'receivers': json.dumps(receivers)}
#         return render(request, 'PostMessage.html', context)

# def PostMessageAction(request):
#     global username
#     if request.method == 'POST':
#         receiver = request.POST.get('t1', False)
#         msg = request.POST.get('t2', False)
#         today = str(date.today())
#         msg = encrypt(msg)
#         msg = str(base64.b64encode(msg), 'utf-8')
#         msg_id = 0
#         con = pymysql.connect(host='localhost', port=3306, user='root', password='123456789', database='irisauth', charset='utf8')
#         with con:
#             cur = con.cursor()
#             cur.execute("select max(msg_id) FROM messages")
#             rows = cur.fetchall()
#             for row in rows:
#                 msg_id = row[0]
#         if msg_id is not None:
#             msg_id = msg_id + 1
#         else:
#             msg_id = 1
#         db_connection = pymysql.connect(host='localhost', port=3306, user='root', password='123456789', database='irisauth', charset='utf8')
#         db_cursor = db_connection.cursor()
#         student_sql_query = "INSERT INTO messages(msg_id, sender, receiver, message, msg_date) VALUES(%s, %s, %s, %s, %s)"
#         db_cursor.execute(student_sql_query, (msg_id, username, receiver, msg, today))
#         db_connection.commit()
#         output = "Encrypted Msg = " + msg + "<br/>"
#         output += "Message ID = " + str(msg_id) + "<br/>"
#         output += "Message Sent to Receiver : " + receiver + "<br/>"
#         context = {'data': output}
#         return render(request, 'PostMessage.html', context)
import json
import base64
import pymysql
from datetime import date
from django.shortcuts import render
#from .encryption_module import encrypt  # Ensure you have this module for encryption

# Global variable for username
username = None
def get_database_connection():
    """Function to get database connection"""
    return pymysql.connect(host='localhost', port=3306, user='root', password='123456789', database='irisauth', charset='utf8')

def PostMessage(request):
    context = {'receivers': json.dumps([])}
    return render(request, 'PostMessage.html', context)

def search_receivers(request):
    global username
    if request.method == 'GET':
        query = request.GET.get('query', '').strip()
        receivers = []
        if query:
            try:
                with get_database_connection() as con:
                    with con.cursor() as cur:
                        cur.execute("SELECT username FROM register WHERE username LIKE %s", (f'%{query}%',))
                        rows = cur.fetchall()
                        receivers = [row[0] for row in rows if row[0] != username]
            except pymysql.MySQLError as e:
                print(f"Error fetching receivers: {e}")
        return JsonResponse(receivers, safe=False)
    
# def get_database_connection():
#     """Function to get database connection"""
#     return pymysql.connect(host='localhost', port=3306, user='root', password='123456789', database='irisauth', charset='utf8')

# def PostMessage(request):
#     global username
#     if request.method == 'GET':
#         receivers = []
#         try:
#             with get_database_connection() as con:
#                 with con.cursor() as cur:
#                     cur.execute("SELECT username FROM register")
#                     rows = cur.fetchall()
#                     receivers = [row[0] for row in rows if row[0] != username]
#         except pymysql.MySQLError as e:
#             print(f"Error fetching receivers: {e}")

#         context = {'receivers': json.dumps(receivers)}
#         return render(request, 'PostMessage.html', context)

def PostMessageAction(request):
    global username
    if request.method == 'POST':
        receiver = request.POST.get('t1', '').strip()
        msg = request.POST.get('t2', '').strip()
        today = str(date.today())

        if not receiver or not msg:
            context = {'data': 'Receiver and Message cannot be empty.'}
            return render(request, 'PostMessage.html', context)

        # Encrypt the message
        encrypted_msg = encrypt(msg)
        encoded_msg = base64.b64encode(encrypted_msg).decode('utf-8')

        msg_id = None
        try:
            with get_database_connection() as con:
                with con.cursor() as cur:
                    cur.execute("SELECT MAX(msg_id) FROM messages")
                    msg_id = cur.fetchone()[0]

            msg_id = (msg_id + 1) if msg_id is not None else 1

            with get_database_connection() as db_connection:
                with db_connection.cursor() as db_cursor:
                    student_sql_query = """
                        INSERT INTO messages (msg_id, sender, receiver, message, msg_date) 
                        VALUES (%s, %s, %s, %s, %s)
                    """
                    db_cursor.execute(student_sql_query, (msg_id, username, receiver, encoded_msg, today))
                    db_connection.commit()

            output = f"Encrypted Msg = {encoded_msg}<br/>"
            output += f"Message ID = {msg_id}<br/>"
            output += f"Message Sent to Receiver: {receiver}<br/>"
        except pymysql.MySQLError as e:
            output = f"Error while posting the message: {e}"

        context = {'data': output}
        return render(request, 'PostMessage.html', context)
   
##################     LOGIN    ##################
# import cv2
# import numpy as np


def compare_iris(image1_path, image2_path):
    image1 = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)
    image2 = cv2.imread(image2_path, cv2.IMREAD_GRAYSCALE)
    
    if image1.shape != image2.shape:
        return False
    
    difference = cv2.absdiff(image1, image2)
    result = not np.any(difference)  # If difference is all zeros, images are the same
    return result

def ExtractMessage(username):
    secret = "not exists"
    registered_image_path = 'IrisAuthApp/static/watermark/' + username + "_original.png"
    test_image_path = "IrisAuthApp/static/test.png"
    
    if os.path.exists('IrisAuthApp/static/watermark/'+username+".png"):
        if compare_iris(test_image_path, registered_image_path):
            secret = crypto_steganography.retrieve('IrisAuthApp/static/watermark/' + username + ".png")
        os.remove("IrisAuthApp/static/test.png")
        
    return secret

# from django.core.files.storage import FileSystemStorage
# import pymysql

def UserLogin(request):
    global username
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        image = request.FILES['t3']
        message = request.POST.get('t4', False)
        
        if os.path.exists("IrisAuthApp/static/test.png"):
            os.remove("IrisAuthApp/static/test.png")
        
        fs = FileSystemStorage()
        fs.save("IrisAuthApp/static/test.png", image)
        
        status = "failed"
        con = pymysql.connect(host='localhost', port=3306, user='root', password='123456789', database='irisauth', charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select username, password FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username and row[1] == password:
                    status = 'success'
                    break
        
        if status == 'success':
            output = 'Login Details Matched'
            extract_msg = ExtractMessage(username)
            if extract_msg == message:
                status = 'WELCOME ' + username + " <br> Both Login & Iris Watermark Authentication is Successful"
                context = {'data': status}
                return render(request, 'UserScreen.html', context)
            else:
                context = {'data': 'Iris image does not match. Please resubmit.'}
                return render(request, 'Login.html', context)
        else:
            context = {'data': 'Invalid username or password'}
            return render(request, 'Login.html', context)

        
# def ExtractMessage(username, message):
#     secret = "not exists"
#     if os.path.exists('IrisAuthApp/static/watermark/'+username+".png"):
#         img1 = open("IrisAuthApp/static/test.png","rb").read()
#         img2 = open('IrisAuthApp/static/watermark/'+username+"_original.png","rb").read()
#         if img1 == img2:
#             secret = crypto_steganography.retrieve('IrisAuthApp/static/watermark/'+username+".png")
#         os.remove("IrisAuthApp/static/test.png")        
#     return secret

# def UserLogin(request):
#     global username
#     if request.method == 'POST':
#         username = request.POST.get('t1', False)
#         password = request.POST.get('t2', False)
#         image = request.FILES['t3']
#         message = request.POST.get('t4', False)
#         if os.path.exists("IrisAuthApp/static/test.png"):
#             os.remove("IrisAuthApp/static/test.png")
#         fs = FileSystemStorage()
#         fs.save("IrisAuthApp/static/test.png", image)
#         status = "failed"
#         con = pymysql.connect(host='localhost',port = 3306,user = 'root', password = '123456789', database = 'irisauth',charset='utf8')
#         with con:
#             cur = con.cursor()
#             cur.execute("select username,password FROM register")
#             rows = cur.fetchall()
#             for row in rows:
#                 if row[0] == username and row[1] == password:
#                     status = 'success'
#                     break
#         if status == 'success':
#             output = 'Login Details Matched'
#             extract_msg = ExtractMessage(username, message)
#             if extract_msg == message:
#                 #status = 'Welcome username : '+username+"<br/>Both Logging & Iris Watermark Authentication Successfull"
#                 status = ""
#                 context= {'data':status}
#                 return render(request, 'UserScreen.html', context)
#             else:
#                 context= {'data':'Watermark Authentication Failed'}
#                 return render(request, 'Login.html', context)
#         else:
#             context= {'data':'Invalid username'}
#             return render(request, 'Login.html', context)

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Login(request):
    if request.method == 'GET':
       return render(request, 'Login.html', {})

########### ###########  Register ########### ########### ########### ########### 

# def watermarkImage(user, message):
#     img = cv2.imread('IrisAuthApp/static/watermark/'+user+"_original.png")
#     img = cv2.resize(img,(128,128), interpolation=cv2.INTER_CUBIC)
#     gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     answer = find_iris(gray_img, daugman_start=10, daugman_end=30, daugman_step=1, points_step=3)
#     iris_center, iris_rad = answer
#     start = iris_center[0]
#     end = iris_center[1]
#     radius = iris_rad
#     result = img[start-radius:start+radius,end-radius:end+radius]
#     result = cv2.resize(result, (64,64), interpolation=cv2.INTER_CUBIC)
#     segmented = result
#     if os.path.exists('IrisAuthApp/static/watermark/'+username+".png"):
#         os.remove('IrisAuthApp/static/watermark/'+username+".png")
#     cv2.imwrite('IrisAuthApp/static/watermark/iris.png', segmented)    
#     crypto_steganography.hide('IrisAuthApp/static/watermark/iris.png', 'IrisAuthApp/static/watermark/'+user+".png", message)
#     if os.path.exists("IrisAuthApp/static/watermark/iris.png"):
#         os.remove("IrisAuthApp/static/watermark/iris.png")


# from inference_sdk import InferenceHTTPClient



# import cv2
# import supervision as sv

# def validate_eye_image(image_path: str,user):
#     # Use the Roboflow API to detect if the image contains an eye
#     result = CLIENT.infer(image_path, model_id="eye-data/1")
#     result1 = CLIENT.infer(image_path, model_id="eyessee-v2/4")
#     print(result, "ERTYTUI")
#     print( "###############################ERTYTUI")
#     print(result1, "ERTYTUI")
#     # print(result['predictions'], "result['predictions']")

#     # Load the image using OpenCV
#     image = cv2.imread(image_path)
#     detections = sv.Detections.from_inference(result)

#     label_annotator = sv.LabelAnnotator()
#     bounding_box_annotator = sv.BoundingBoxAnnotator()

#     annotated_image = bounding_box_annotator.annotate(
#         scene=image, detections=detections)
#     annotated_image = label_annotator.annotate(
#         scene=annotated_image, detections=detections)
    
#     # detection = sv.Detections.from_inference(result1)

#     # label_annotato = sv.LabelAnnotator()
#     # bounding_box_annotato = sv.BoundingBoxAnnotator()

#     # annotated_imag = bounding_box_annotato.annotate(
#     #     scene=image, detections=detection)
#     # annotated_imag = label_annotato.annotate(
#     #     scene=annotated_imag, detections=detection)
#     if result['predictions']:
#         # Eye detected, return the image data
#         # Create a folder to store images for the user
#         user_folder = 'IrisAuthApp/static/Registered/user_images/' + user
#         if not os.path.exists(user_folder):
#             os.makedirs(user_folder)

#         # Save eye detected image in the user's folder
#         eye_detected_path = os.path.join(user_folder, user + "_eye_detected.png")
#         cv2.imwrite(eye_detected_path, annotated_image)

#         image = cv2.imread(image_path)
#         detection = sv.Detections.from_inference(result1)
#         label_annotato = sv.LabelAnnotator()
#         bounding_box_annotato = sv.BoundingBoxAnnotator()
#         annotated_imag = bounding_box_annotato.annotate(
#             scene=image, detections=detection)
#         annotated_imag = label_annotato.annotate(
#             scene=annotated_imag, detections=detection)

#         # Save iris detected image in the user's folder
#         iris_detected_path = os.path.join(user_folder, user + "_iris_detected.png")
#         cv2.imwrite(iris_detected_path, annotated_imag)

#         return True
#     else:
#         # No eye detected, return False and None for the image
#         return False, None
    

# import cv2
# import numpy as np
# from inference_sdk import InferenceHTTPClient

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="2RMVvZlyCc8ul2sDr9rf"
)


# import cv2
# import supervision as sv

def validate_eye_image(image_path: str, user: str):
    
    # Use the Roboflow API to detect if the image contains an eye
    result = CLIENT.infer(image_path, model_id="human-eye-detection/1")
    print(result,"vbnjkl;")

    # # Load the image using OpenCV
    # image = cv2.imread(image_path)
    # detections = sv.Detections.from_inference(result)

    # label_annotator = sv.LabelAnnotator()
    # bounding_box_annotator = sv.BoundingBoxAnnotator()

    # annotated_image = bounding_box_annotator.annotate(scene=image, detections=detections)
    # annotated_image = label_annotator.annotate(scene=annotated_image, detections=detections)

    if result['predictions']:
        print("helooooooooooooooooooooo")
        # Create a folder to store images for the user
        user_folder = f'IrisAuthApp/static/Registered/user_images/{user}'
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        # Save eye detected image in the user's folder
        eye_detected_path = os.path.join(user_folder, f"{user}_eye_detected.png")
        # cv2.imwrite(eye_detected_path, annotated_image)

        # Annotate and save the iris detected image
        image = cv2.imread(image_path)
        # detection = sv.Detections.from_inference(result1)
        # annotated_image = bounding_box_annotator.annotate(scene=image, detections=detection)
        # annotated_image = label_annotator.annotate(scene=annotated_image, detections=detection)

        # iris_detected_path = os.path.join(user_folder, f"{user}_iris_detected.png")
        # cv2.imwrite(iris_detected_path, annotated_image)

        return True
    else:
        return False


def watermark_image(user: str, message: str):
    try:
        # Read and process the original image
        img = cv2.imread(f'IrisAuthApp/static/watermark/{user}_original.png')
        img = cv2.resize(img, (128, 128), interpolation=cv2.INTER_CUBIC)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(f'IrisAuthApp/static/watermark/{user}_gray.png', gray_img)

        answer = find_iris(gray_img, daugman_start=10, daugman_end=30, daugman_step=1, points_step=3)
        iris_center, iris_rad = answer
        start = iris_center[0]
        end = iris_center[1]
        radius = iris_rad
                # Segment the iris region from the original resized image
        start_x = max(0, start - radius)
        end_x = min(img.shape[1], start + radius)
        start_y = max(0, end - radius)
        end_y = min(img.shape[0], end + radius)
        result = img[start_y:end_y, start_x:end_x]
        result = cv2.resize(result, (64, 64), interpolation=cv2.INTER_CUBIC)
        # result = img[start-radius:start+radius, end-radius:end+radius]
        # result = cv2.resize(result, (128, 128), interpolation=cv2.INTER_CUBIC)

        if os.path.exists(f'IrisAuthApp/static/watermark/{user}.png'):
            os.remove(f'IrisAuthApp/static/watermark/{user}.png')

        cv2.imwrite(f'IrisAuthApp/static/watermark/iris.png', result)
        crypto_steganography.hide(f'IrisAuthApp/static/watermark/iris.png', f'IrisAuthApp/static/watermark/{user}.png', message)
        cv2.imwrite(f'IrisAuthApp/static/watermark/{user}_watermarked.png', cv2.imread(f'IrisAuthApp/static/watermark/{user}.png'))

        if os.path.exists("IrisAuthApp/static/watermark/iris.png"):
            os.remove("IrisAuthApp/static/watermark/iris.png")

        # Save images in the user's folder
        user_folder = f'IrisAuthApp/static/Registered/user_images/{user}'
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        cv2.imwrite(os.path.join(user_folder, f"{user}_original.png"), cv2.imread(f'IrisAuthApp/static/watermark/{user}_original.png'))
        cv2.imwrite(os.path.join(user_folder, f"{user}_gray.png"), cv2.imread(f'IrisAuthApp/static/watermark/{user}_gray.png'))
        cv2.imwrite(os.path.join(user_folder, f"{user}_watermarked.png"), cv2.imread(f'IrisAuthApp/static/watermark/{user}_watermarked.png'))
    except Exception as e:
        print(f"Error during watermarking: {e}")

def RegisterAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        image = request.FILES['t6']
        message = request.POST.get('t7', False)

        fs = FileSystemStorage()
        image_path = f'IrisAuthApp/static/watermark/{username}_original.png'
        if os.path.exists(image_path):
            os.remove(image_path)
        fs.save(image_path, image)

        if not validate_eye_image(image_path, username):
            context = {'data': 'Uploaded image is not a valid iris image. Please upload a proper iris image.'}
            return render(request, 'Register.html', context)

        output = "none"
        con = pymysql.connect(host='localhost', port=3306, user='root', password='123456789', database='irisauth', charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("SELECT username FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username:
                    output = f"{username} Username already exists"

        if output == "none":
            db_connection = pymysql.connect(host='localhost', port=3306, user='root', password='123456789', database='irisauth', charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO register(username, password, contact, email, address) VALUES(%s, %s, %s, %s, %s)"
            db_cursor.execute(student_sql_query, (username, password, contact, email, address))
            db_connection.commit()

            if db_cursor.rowcount == 1:
                watermark_image(username, message)
                context = {'data': 'Signup Process Completed'}
            else:
                context = {'data': 'Error in signup process'}
        else:
            context = {'data': output}

        return render(request, 'Register.html', context)
