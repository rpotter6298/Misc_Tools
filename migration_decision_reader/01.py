import os
from PIL import Image
from pdf2image import convert_from_path
import pandas as pd
import pytesseract
from datetime import datetime
from pathlib import Path
import json

local_config =  json.loads(open(Path.home() / ".migration_decision_reader" / "local_config.json").read())
#print(local_config['poppler_path'])
#tesseract_path = r"C:\Users\potr\AppData\Local\Tesseract-OCR\tesseract.exe"
#pytesseract.pytesseract.tesseract_cmd = tesseract_path
pytesseract.pytesseract.tesseract_cmd = fr"{str(Path(local_config['tess_path']) / 'tesseract.exe')}"
#print(pytesseract.pytesseract.tesseract_cmd)

# os.chdir("migration_decision_reader")

def break_pdf(pdf):
    pdfs = Path(pdf)
    name = pdf.split("\\")[-1].split(".")[0]
    pages = convert_from_path(pdfs, 350, poppler_path = fr"{str(Path(local_config['poppler_path']) / 'bin')}")
    i = 1
    for page in pages:
        image_name = "Page_" + str(i) + ".jpg"
        page.save("working_images/" + name +"_"+ image_name, "JPEG")
        i = i + 1


def build_infodic(im, rotate=False):
    im = Image.open(im)
    if rotate==True:
        im = im.rotate(180)
    imwidth, imheight = im.size
    ### Date Region
    box = (imwidth / 3, imheight / 12, 2 * (imwidth / 3), imheight / 8)
    cimg = im.crop(box)
    text = str(pytesseract.image_to_string(cimg, lang="swe")).split("\n")
    for item in text:
        try:
            dt = datetime.strptime(item.replace(" ", ""), "%Y—%m—%d")
        except:
            pass
    date = dt.strftime("%Y%m%d")

    # cimg.save("test.jpg")
    ### Decision Number
    box = (2 * (imwidth / 3), imheight / 12, imwidth, imheight / 6)
    cimg = im.crop(box)
    text = str(pytesseract.image_to_string(cimg, lang="swe")).split("\n")
    text = [x for x in text if x]
    decisionno = text[1]
    ### Main Body
    box = (200, imheight / 4, imwidth - 200, imheight - imheight / 8)
    cimg = im.crop(box)
    text = str(pytesseract.image_to_string(cimg, lang="swe")).split("\n")
    text = [x for x in text if x]
    seekeri = [idx for idx, s in enumerate(text) if "Sökande" in s][0]
    decisioni = [idx for idx, s in enumerate(text) if "Beslut" in s][0]
    embassyi = [idx for idx, s in enumerate(text) if "Beslut skickat till" in s][0]
    try:
        copyi = [idx for idx, s in enumerate(text) if "Kopia till" in s][0]
    except:
        copyi = None
    seeker = text[seekeri:decisioni]
    decision = text[decisioni:embassyi]
    embassy = text[embassyi:copyi]

    ### Decision Logic
    seeker = (','.join(seeker)).split(",")
    seeker = [x for x in seeker if x]
    if any("bevilja" in term for term in decision):
        fdecision = "Admitted"
    elif any("avslå" in term for term in decision):
        fdecision = "Denied"
    elif any("avskriva" in term for term in decision):
        fdecision = "Discontinued" 
    else:
        fdecision = "Unclear (Read Error)"
    nationality = [i for i in seeker if "medborgare i" in i][0]
    birthdate = [i for i in seeker if "född" in i][0]
    sex = seeker[[idx for idx, s in enumerate(seeker) if "född" in s][0]+1]
    address = " ".join(seeker[[idx for idx, s in enumerate(seeker) if "Adress:" in s][0]:])
    
    ## Info Aggregation
    infodic = {
        "date": date,
        "decision_no": decisionno,
        "last_name": seeker[1].lstrip(),
        "first_name": seeker[2].lstrip(),
        "birth_date": birthdate.replace("född", "").lstrip(),
        "sex": sex.lstrip(),
        "nationality": nationality.replace("medborgare i", "").lstrip(),
        "address": address.replace("Adress:", "").lstrip(),
        "decision": fdecision,
        "embassy": embassy[1],
    }
    return infodic


def main():
    df = pd.DataFrame()
    for file in os.listdir("pdf_files"):
        print("Breaking apart PDF: "+os.path.join("pdf_files", file))
        break_pdf(os.path.join("pdf_files", file))
        print("pdf broken")
    
    for image in os.listdir("working_images"):
        #print(image)
        rotate = False
        if image.endswith(".jpg"):
            #Image.open(Path("working_images") / image).show()
            print("Building Dataframe...")
            print(image)
            count = 0
            while True: 
                #print("loop1")
                #print(image)
                
                try:
                    info = build_infodic("working_images\\" + image, rotate=rotate)
                    df = pd.concat([df, pd.DataFrame([info])], ignore_index=True)
                    print(df)
                    break
                except Exception as error:
                    if count == 0:
                        rotate=True
                        continue
                    else:
                        print("Error, could not process document. Please enter manually.")
                        Image.open(Path("working_images") / image).show()
                        option = input("Enter 'retry' to retry or 'skip' to skip: ")
                        if option == 'retry':
                            continue
                        else:
                            break
            #print(info)

    #print(df)
    input("Dataframe Complete. Press enter to write file.")
    df.to_excel("excel_outputs\\Output_" + datetime.today().strftime("%Y%m%d%H%M%S") + ".xlsx", index=False)

    print("File Written. Cleaning up...")
    ## Cleanup
    for image in os.listdir("working_images"):
        os.remove("working_images\\"+image)
    for pdf in os.listdir("pdf_files"):
        try:
            Path("pdf_files\\"+pdf).rename("archive_pdf\\"+pdf)
        except Exception:
            #print("error")
            if os.path.exists("archive_pdf\\"+pdf):
                #print("Exists")
                #decision == 0
                while True:
                    decision = input("File:" + pdf+ " exists in archive. Confirm that the file is the same? Input Yes or No:  ")
                    if decision in ["Yes","yes", "Y", "y"]:
                        os.remove("pdf_files\\"+pdf)
                        break
                    if decision in ["No", "no", "n", "N"]:
                        input("Please rename the file in the archive and then press enter.")
                        try:
                            Path("pdf_files\\"+pdf).rename("archive_pdf\\"+pdf)
                        except Exception:
                            input("Error Encountered, please get help with troubleshooting.")
                        break
                    else:
                        print("Invalid response")
            else:
                input ("I don't know what happened. Please get help with troubleshooting.")
    input("Process complete. Press enter to exit.")
main()

