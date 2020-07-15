import os
import math
import zipfile
import cv2 as cv
import pytesseract
import numpy as np
from kraken import pageseg
from PIL import Image, ImageDraw, ImageFont
from IPython.display import display # for cousera

MAX_SIZE = (180, 180)
font_file = "./readonly/fanwood-webfont.ttf"

def extract_zip (zip_file) :
    '''Function that returns a list with the .png files extracted
    from a zip file.
        arg: zip_file , name of the zip file that contains the png files
        ret: a list of the names of the .png extracted file '''
    
    with zipfile.ZipFile('./readonly/small_img.zip', 'r') as zip_ref:
        zip_ref.extractall('./')
    return [file for file in os.listdir() if file[-4:]=='.png']

def get_text(image):
    '''Function that receives as an argument an PIL Image object 
    and returns a string with the text inside the Image using the
    pageseg function from the kraken module'''

    # get the list of the coordinates of the boxes that contain text
    page_boxes = pageseg.segment( image.convert('1') )['boxes'] 
    # get the text
    text = ''
    for box in page_boxes :
        x,y,width,height = box
        cropped_image = image.crop(box)
        # the string its addend with a whitespace
        text += ' '+pytesseract.image_to_string( cropped_image )
    return text
        
def check_word(image, word):
    '''Function that return a boolean values 'True' if the word 
    passed as argument appears in the PIL Image object. If not, 
    returns 'False'. ''' 
    if word in get_text(image).lower() :
        return True
    else : 
        return False
    
def get_faces(image):
    '''Function that returns a list of the faces (as PIL Image objects) 
    detected in the image passed as argument (also as PIL Image). '''

    # transform the Image PIL object into a nparray in grey scale
    image_cv = np.asarray(image)
    image_cv_gray = cv.cvtColor(image_cv, cv.COLOR_BGR2GRAY)
    image = Image.fromarray(image_cv_gray, "L")
    # get a list of the faces that have been recognized in the image
    faces = face_cascade.detectMultiScale(image_cv_gray)
    # get a PIL Image Object (the faces will be cut out from here)
    pil_img=Image.fromarray(image_cv_gray,mode="L")
    images_faces = [] # list with the PIL Image faces
    for x,y,w,h in faces: # faces detected are turned as (x, y, width, heigh)
        images_faces.append(pil_img.crop((x,y,x+w,y+h)))
    return images_faces

def add_text(image, file_name, no_faces=False):
    ''' Function that returns an PIL Image PIL Object with corresponding text according to the value of no_faces
    Example :
        no_faces=False -> text = 'Results found in file file_name'
        no_faces=True  -> text = 'Results found in file file_name
                                  But there were no faces in that file!'     '''

    font = ImageFont.truetype(font_file, 40)
    draw = ImageDraw.Draw(image)
    draw.text((0, 0),'Results found in file {}'.format(file_name),255,font=font)
    if no_faces == True :
        draw.text((0, 80),'But there were no faces in that file!',255,font=font)
    return image 
    
# receives as an argument a list of the faces (PIL IMAGE) an return a PIL IMAGE conctact_sheet
def get_contact_sheet(faces, file_name) :
    
    # create the contact sheet
    n_columns = math.ceil(len(faces)/5)
    contact_sheet = Image.new('L', (MAX_SIZE[0]*5,MAX_SIZE[1]*n_columns))
    #if there's no faces
    if len(faces) == 0 : return add_text(contact_sheet, file_name, no_faces=True)
    # If not, resize the images
    faces = [face.resize(MAX_SIZE) for face in faces]
    mode_type = faces[0].mode # to create the contact_sheet
    # Paste the images
    index = 0 # for the list of the faces
    for y in range(0, MAX_SIZE[1]*n_columns, MAX_SIZE[1]):
        if index == len(faces) : break # if the index is out of the list range
        for x in range(0, MAX_SIZE[0]*5, MAX_SIZE[0]):
            if index == len(faces) : break # if the index is out of the list range
            contact_sheet.paste(faces[index], (x,y) )
            index += 1
    return add_text(contact_sheet, file_name)
            
            
    
face_cascade = cv.CascadeClassifier('readonly/haarcascade_frontalface_default.xml')
eye_cascade = cv.CascadeClassifier('readonly/haarcascade_eye.xml')
zip_file_name = './readonly/small_img.zip'
word = 'for'
############### MAIN FUNCTION #################

files = extract_zip(zip_file_name)
print('Files extracted : ', files)
#images = [Image.open(file) for file in files] # list of Image objects

file_names = ['im1.jpg', 'im2.jpg'] # used to tests
images = [Image.open('im1.jpg'), Image.open('im2.jpg')] # for test
# images to be scanned
for image in images : 
    display(image)
# ----for each image file (each page)---

# CHECK IF THE WORD IN A CERTAIN PAGE
#for image in images :
#    print('-----')
#    print(check_word(image, word))

# GET A LIST WITH THE FACES OF AN PIL IMAGE
# each sublist has the face of each page
page_faces = [get_faces(image) for image in images]
contact_sheets = []

print(page_faces)
for index in range(len(page_faces)) :
    contact_sheets.append(get_contact_sheet(page_faces[index], file_names[index]))

for contact_sheet in contact_sheets:
    display(contact_sheet)
    