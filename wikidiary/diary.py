import re
from datetime import datetime
from wikidiary import Wiki
from pathlib import Path
from dateutil import tz
import csv


def replaceumlaut(txt):
    txt = txt.replace("Ä","AE")
    txt = txt.replace("Ö","OE")
    txt = txt.replace("Ü","UE")
    txt = txt.replace("ä","ae")
    txt = txt.replace("ö","oe")
    txt = txt.replace("ü","ue")
    txt = txt.replace("ß","ss")
    txt = txt.replace(":_","_dp_")
    return(txt)


def containsObject(obj, list) :
    for i in list:
        if (i == obj):
            return True
    return False

def uniqueLines(file):
    lines_seen = set() # holds lines already seen
    outpath = "/tmp/unique.txt"
    outfile = open(outpath, "w")
    for line in open(file, "r"):
        if line not in lines_seen: # not a duplicate
            outfile.write(line)
            lines_seen.add(line)
    outfile.close()
    shutil.copyfile(outpath, file) #copy src to dst


def correct_title(title):
    with open('meta/podcast/name_mapping.txt', 'r') as file:
        reader = csv.DictReader(file,delimiter="\t")
        for row in reader:
            wrong = row["original_title"]
            correct = row["correct_title"]

            if(title==wrong):
                #print("CORRECT! - "+ wrong + " to " + correct)
                return(correct)
    return(title)


class DiaryBox:
    array =[]
    tag_array = {}
    isarray = False
    client=""
    message_type=""
    message = ""
    listed = False
    title=""
    folge=""
    link=""
    text=""
    von=""
    verwendungszweck=""
    count = ""
    source="Lastschrift"
    ID = ""
    format = "jpg"
    inside=""
    tag ="Ausgabe"
    content = ""
    date = ""
    end=""
    laden = ""
    lines = ""
    media = ""
    speaker = []
    nach=""
    fact_tags = []

    # reading
    page_start=""
    page_end=""
    pages_read = ""
    precontent=""

    price = ""
    start=""
    type_text=""
    header = "{{\n"
    footer = "}}"
    type_text=""
    date_string=""
    string = ""
    photo=False
    echo=False
    noPhoto = False
    upload = False
    printed = False
    type=""
    box_array = []
    abfahrt = ""
    ankunft = ""
    linie=""
    verspätung=""
    richtung=""
    special=""



    def __init__(self):
        print("")
        self.tag_array = {}
        self.content = ""
#    def __init__(self,type):
#        self.type = type
    def setFromTelegramMessage(self,message):
        self.photo=message.photo
        self.media = message.media
        #self.date = message.date  + timedelta(hours=2)
        self.date = message.date.astimezone(tz.tzlocal())
        self.date_string = datetime.strftime(self.date,"%Y-%m-%d")
        self.time = datetime.strftime(self.date,"%H:%M")
        self.message = message
        self.box_from_text(message.text)
        #self.tag_array = ""

    def check_abbrv(self,line):
        shops = ["Nahkauf","Aldi","DM"]
        match = False
        for shop in shops:
            if(re.search("^"+shop+":",line)):
                match = True
        if match:
            self.type = "Einkauf"
            args = line.split(":")
            self.laden = args[0]
            self.tag = "Lebensmittel"
            self.price = float(args[1])
            return True

        photos = ["Photo"]
        match = False
        for photo in photos:
            if(re.search("^"+photo+":",line)):
                match = True
        if match:
            self.type = "Photo"
            self.photo = True
            args = line.split(":")
            #self.laden = args[0]
            self.title = args[1]
            return True


        return False

    def box_from_text(self,text):
        i = 0
        lines = text.splitlines()
        for line in lines:
            line = line.strip()
            if self.check_abbrv(line):
                next
            elif re.search("^\+",line):
                message_type=line
                message_type = re.sub("^\+","",message_type).strip()
                self.type = message_type
            elif re.search("\+PodcastAddict",line):
                message_type="Podcast"
                self.type = message_type
            elif re.search("^#",line):
                message_type=line
                message_type = re.sub("#","",message_type).strip()
                self.title = message_type
                if self.type!="Tags":
                    self.type = "Tag"
                self.time = "00:00"
            elif re.search("^/",line):
            	self.content = self.content
            elif re.search("^___",line):
                restlines = lines[i+1:len(lines)]
                restlines = "\n".join(restlines)
                box = DiaryBox()
                box.date = self.date.astimezone(tz.tzlocal())
                box.date_string = datetime.strftime(self.date,"%Y-%m-%d")
                box.time = datetime.strftime(self.date,"%H:%M")
                box.message = self.message
                box.message.text = restlines
                box.box_from_text(restlines)
                #self.addBox(box)
                self.box_array = self.box_array + [box]
                #print(box.toString())
                print(box.message.text)
                #print(restlines)
                break
            elif re.search("^Abfahrt:",line):
            	self.abfahrt = re.sub("^Abfahrt:","",line).strip()
            elif re.search("^Ankunft:",line):
                self.ankunft = re.sub("^Ankunft:","",line).strip()
            elif re.search("^Echo",line):
            	self.echo = True
            elif re.search("^noPhoto",line):
            	self.noPhoto = True
            elif re.search("^NoPhoto",line):
            	self.noPhoto = True
            elif re.search("^nophoto",line):
            	self.noPhoto = True
            elif re.search("^Title",line):
                title=line
                title = re.sub("^Title:","",title).strip()
                self.title = title
            elif re.search("^Format",line):
                format = re.sub("^Format:","",line).strip()
                self.format = format
            elif re.search("^Date",line):
                print("")
                # date=line
                # date = re.sub("^Date:","",date).strip()
                # if(date=="Gestern"):
                #     date = self.date-timedelta(days=1)
                #     date = datetime.strptime(date,"%Y-%m-%d")
                # self.date_string =date
                # self.date = datetime.strptime(date,"%Y-%m-%d")
            elif re.search("^Photo",line):
                self.photo = True
            elif re.search("^Tag",line):
                tag = re.sub("^Tag:","",line).strip()
                self.tag = tag
                fact_tag=tag
                fact_tag = re.sub("^Tag:","",fact_tag).strip()
                self.fact_tags.append(fact_tag)
            elif re.search("^Type",line):
                type_text=line
                type_text = re.sub("^Type:","",type_text).strip()
                self.type_text = type_text
            elif re.search("^ID",line):
                ID = re.sub("^ID:","",line).strip()
                self.ID = ID
            elif re.search("^Inside",line):
                inside = re.sub("^Inside:","",line).strip()
                self.inside = inside
            elif re.search("^Laden",line):
                laden = re.sub("^Laden:","",line).strip()
                self.laden = laden
            elif re.search("^Laden",line):
                laden = re.sub("^Laden:","",line).strip()
                self.laden = laden
            elif re.search("^Time",line):
                time = re.sub("^Time:","",line).strip()
                self.time = time
            elif re.search("^Preis",line):
                price = re.sub("^Preis:","",line).strip()
                self.price = price
            elif re.search("^Count",line):
                count=line
                count = re.sub("^Count:","",count).strip()
                self.count = count
            elif re.search("^Link",line):
                link=line
                link = re.sub("^Link:","",link).strip()
                self.link = link
            elif re.search("^Folge",line):
                folge=line
                folge = re.sub("^Folge:","",folge).strip()
                self.folge = folge
            elif re.search("^Speaker",line):
                speaker = re.sub("^Speaker:","",line).strip()
                self.speaker.append(speaker)
            elif re.search("^Verwendungszweck",line):
                verwendungszweck=line
                verwendungszweck = re.sub("^Verwendungszweck:","",verwendungszweck).strip()
                self.verwendungszweck = verwendungszweck
            elif re.search("^Von",line):
                von=line
                von = re.sub("^Von:","",von).strip()
                self.von = von
            elif re.search("^Verspätung",line):
                vers=line
                vers = re.sub("^Verspätung:","",vers).strip()
                self.verspätung = vers
            elif re.search("^Linie",line):
                linie=line
                linie = re.sub("^Linie:","",linie).strip()
                self.linie = linie
            elif re.search("^Nummer",line):
                linie=line
                linie = re.sub("^Nummer:","",linie).strip()
                self.linie = linie
            elif re.search("^Special",line):
                special=line
                special = re.sub("^Special:","",special).strip()
                self.special = special
            elif re.search("^Richtung",line):
                richtung=line
                richtung = re.sub("^Richtung:","",richtung).strip()
                self.richtung = richtung
            elif re.search("^Nach",line):
                nach=line
                nach = re.sub("^Nach:","",nach).strip()
                self.nach = nach
            elif re.search("^Seite_start",line):
                page_start=line
                page_start = re.sub("^Seite_start:","",page_start).strip()
                self.page_start = page_start
            elif re.search("^Seite_end",line):
                page_end=line
                page_end = re.sub("^Seite_end:","",page_end).strip()
                self.page_end = page_end
            elif re.search("^Start",line):
                start=line
                start = re.sub("^Start:","",start).strip()
                self.start =start
            elif re.search("^Source",line):
                source = re.sub("^Source:","",line).strip()
                self.source = source
            elif re.search("^End",line):
                end=line
                end = re.sub("^End:","",end).strip()
                self.end = end
            elif re.search("^Upload",line):
            	self.upload = True
            elif re.search("^CID",line):
            	print("")
            elif re.search("^MID",line):
            	print("")
            else:
                if re.search("^Place:",line):
                    self.add_to_tags(key="place",value=re.sub("^Place:","",line).strip())
                if re.search("^Person:",line):
                    self.add_to_tags(key="person",value=re.sub("^Person:","",line).strip())
                if re.search("^Zutat:",line):
                    #print("Essen!")
                    self.add_to_tags(key="essen",value=re.sub("^Zutat:","",line).strip())
                self.content = self.content + line + "\n"
            i = i+1
        try:
            self.postSetup()
        except Exception as e:
            print("Error in " + self.title)

    def postSetup(self):
        if self.type=="Arbeit":
            self.header = "{{Arbeit|"+"\n"
            if self.ID =="":
                self.ID = "Arbeit"
            self.title = "Arbeit"
        elif self.type=="Einkauf":
            self.header = "{{Einkauf|laden="+self.laden+ "|price="+ str(self.price) + "|\n"
            self.title = self.laden
        elif self.type=="Event":
            self.header = "{{Event|title="+self.title+"|\n"
        elif self.type=="Information":
            self.header = "{{Information|title="+self.title+"|\n"
        elif self.type=="Fact":
            if self.source != "Lastschrift":
                self.header = "{{Fact|title="+self.title+ "|tags="+ ','.join(self.fact_tags) +"|source="+ self.source +  "|\n"
            else:
                self.header = "{{Fact|title="+self.title+ "|tags="+ ','.join(self.fact_tags) +"|source="+ "" +  "|\n"    
        elif self.type=="Gallery":
            self.photo = True
            date_string = self.date.strftime("%Y-%m-%d")
            img_name = "File:{{#var:date}}"+"_"+self.title.replace(" ", "_")+ self.count + ".jpg"            
            self.add_to_tags(key="gallery",value=img_name)
        elif self.type=="Gastro":
            self.title = self.laden
        elif self.type=="Gedanken":
            self.header = "{{Gedanken|title="+self.title+"|\n"
        elif self.type=="Haushalt":
            self.header = "{{Haushalt|title="+self.title+"|\n"
        elif self.type=="Krankheit":
            self.header = "{{Krankheit|title="+self.title+"|\n"
        elif self.type=="Kochen":
            self.header = "{{Kochen|title="+self.title+"|\n"
        elif self.type=="Lesen":
            self.pages_read = float(self.page_end)-float(self.page_start) + 1
            self.header = "{{Lesen|title="+self.title+"|start=" + self.start + "|end=" + self.end + "|page_start=" + self.page_start + "|page_end=" + self.page_end + "|pages_read=" + str(self.pages_read) + "|\n"
            #self.precontent = "* " + self.start+"\t"+self.end+"\t"+self.page_start+"\t"+self.page_end+"\n"
        elif self.type=="Meeting":
            self.header = "{{Meeting|title="+self.title+"|\n"
        elif self.type=="Migraene":
            self.header = "{{Migraene|\n"
            self.title = "Migraene"
        elif self.type=="Migräne":
            self.header = "{{Migraene|\n"
            self.title = "Migraene"
        elif self.type=="Place":
            self.header = "{{Place|title="+self.title+"|\n"
        elif self.type=="Podcast":
            self.title = correct_title(self.title)
            self.header = "{{Podcast|title="+self.title+"|folge="+self.folge+"|\n"
        elif self.type=="Projekt":
            self.header = "{{Projekt|title="+self.title+"|\n"
        elif self.type=="Spaziergang":
            self.header = "{{Spaziergang|title="+self.title+"|\n"
        elif self.type=="Song":
            self.header = "{{Song|title="+self.title+"|\n"
        elif self.type=="Spiel":
            self.header = "{{Spiel|title="+self.title+"|\n"
        elif self.type=="Sport":
            self.header ="{{Sport|title="+self.title+"|\n"
        elif self.type=="Traum":
            self.header = "{{Traum|title="+self.title+"|\n"
        elif self.type=="Reise":
            self.header = "{{Reise|von="+self.von+"|nach="+self.nach+"|title=Von "+self.von+" nach "+self.nach+"|abfahrt="+self.abfahrt+"|ankunft="+self.ankunft+"|\n"
            self.title = "Reise_" + self.von + "_" + self.nach
        elif self.type=="Tags":
            self.expandTags()
        elif self.type=="Transaktion":
            self.header = "{{Transaktion|von="+self.von+"|nach="+self.nach+"|verwendungszweck="+self.verwendungszweck+"|preis = "+str(self.price)+"|title=Von "+self.von+" nach "+self.nach+"|\n"
            self.title = "Transaktion_" + self.von + "_" + self.nach
        elif self.type=="Video":
            self.header = "{{Video|type="+self.type_text+"|title="+self.title+"|\n"
        elif self.type=="Zug":
            self.header = "{{Zug|von="+self.von+"|nach="+self.nach+"|ankunft="+self.ankunft+"|abfahrt="+self.abfahrt+"|title=Von "+self.von+" nach "+self.nach+"|linie="+self.linie+"|verspätung="+self.verspätung+"|richtung="+self.richtung+"|special="+self.special+"|\n"
            self.title =  "Zug_" + self.von + "_" + self.nach
        elif self.type=="STR":
            self.header = "{{STR|von="+self.von+"|nach="+self.nach+"|ankunft="+self.ankunft+"|abfahrt="+self.abfahrt+"|title=Von "+self.von+" nach "+self.nach+"|linie="+self.linie+"|verspätung="+self.verspätung+"|richtung="+self.richtung+"|\n"
            self.title =  "STR_" + self.von + "_" + self.nach
        elif self.type=="S-Bahn":
            self.header = "{{S-Bahn|von="+self.von+"|nach="+self.nach+"|ankunft="+self.ankunft+"|abfahrt="+self.abfahrt+"|title=Von "+self.von+" nach "+self.nach+"|linie="+self.linie+"|verspätung="+self.verspätung+"|richtung="+self.richtung+"|\n"
            self.title =  "S-Bahn_" + self.von + "_" + self.nach
        elif self.type=="U-Bahn":
            self.header = "{{U-Bahn|von="+self.von+"|nach="+self.nach+"|ankunft="+self.ankunft+"|abfahrt="+self.abfahrt+"|title=Von "+self.von+" nach "+self.nach+"|linie="+self.linie+"|verspätung="+self.verspätung+"|richtung="+self.richtung+"|\n"
            self.title =  "U-Bahn_" + self.von + "_" + self.nach
        elif self.type=="Bus":
            self.header = "{{Bus|von="+self.von+"|nach="+self.nach+"|ankunft="+self.ankunft+"|abfahrt="+self.abfahrt+"|title=Von "+self.von+" nach "+self.nach+"|linie="+self.linie+"|verspätung="+self.verspätung+"|richtung="+self.richtung+"|\n"
            self.title =  "Bus_" + self.von + "_" + self.nach
        elif self.type=="Flug":
            self.header = "{{Flug|von="+self.von+"|nach="+self.nach+"|ankunft="+self.ankunft+"|abfahrt="+self.abfahrt+"|title=Von "+self.von+" nach "+self.nach+"|linie="+self.linie+"|verspätung="+self.verspätung+"|richtung="+self.richtung+"|\n"
            self.title =  "Flug_" + self.von + "_" + self.nach
        elif self.type=="Auto":
            self.header = "{{Auto|von="+self.von+"|nach="+self.nach+"|ankunft="+self.ankunft+"|abfahrt="+self.abfahrt+"|title=Von "+self.von+" nach "+self.nach+"|linie="+self.linie+"|verspätung="+self.verspätung+"|richtung="+self.richtung+"|\n"
            self.title =  "Auto_" + self.von + "_" + self.nach
        elif self.type=="Vortrag":
            self.header = "{{Vortrag|title="+self.title+ "|speaker="+ ','.join(self.speaker) +"|\n"
            self.speaker = []
        if self.type != "Podcast":
            self.upload = True

    def add_to_tags(self,key,value):
        #print("Add to tags")
        if not key in self.tag_array:
            self.tag_array[key] = []
            #self.tag_array[key] = [value]
            self.tag_array[key].append(value)
            #print("Create Key")
        else:
            self.tag_array[key].append(value)
        self.tag_array[key] = list(set(self.tag_array[key]))
        #print(self.tags_toString())
        #if len(self.tag_array[key])>0:
        #self.tag_array[key] = self.tag_array[key].append(value)
        #else:
        #    self.tag_array[key] = [value]

    def tags_toString(self):
        tags = ""
        for key in self.tag_array.keys():
            values = self.tag_array[key]
            for value in values:
                tags = tags + " |Has " + key + " = " + value + "\n"
        return(tags)
    def setListed(self):
        self.listed = True

    def setClient(self,client):
        self.client = client
        for box in self.box_array:
            if box.client=="":
                box.setClient(client)
    def expandTags(self):
        #print("expand")
        self.isarray = True
        lines = self.message.text.splitlines()
        for line in lines:
            line = line.strip()
            if re.search("\+",line):
                message_type=line
                message_type = re.sub("^\+","",message_type).strip()
                #self.type = message_type
            elif re.search("^#",line):
                message_type=line
                message_type = re.sub("#","",message_type).strip()

                b = DiaryBox()
                b.title = message_type
                b.type = "Tag"
                b.time = "00:00"
                b.date = self.date
                b.date_string = self.date_string
                #print("Add Tag " + b.date_string)
                self.array.append(b)



    def toString(self):
        #print("Type: "+ self.type + " - Title: " + self.title)
        msg = ""
        #print(msg + "Tags: "+ str(len(self.tag_array["place"])))
        if self.type=="Arbeit":
            msg = self.generate_general()
        elif self.type=="Ausgabe":
            msg = self.generate_ausgabe_from_template()
        elif self.type=="Einkauf":
            #self.generate_einkauf()
            msg = self.generate_einkauf_from_template()
        elif self.type=="Event":
            #msg = self.generate_event()
            msg = self.generate_general()
        elif self.type=="Gallery":
            msg = self.generate_gallery()
        elif self.type=="Gastro":
            msg = self.generate_gastro_from_template()
        elif self.type=="Photo":
            msg = self.generate_photo()
        elif self.type=="Tag":
            msg = self.generate_tag()
        elif self.type=="":
            #self.generate_reise()
            msg = self.content
        else:
            msg = self.generate_general()
            
            #print("\n")
        self.printed = True
        return(msg)

    def printHeader(self):
        print(self.header)
    def printContent(self):
        print(self.content)

    def printFooter(self):
        print(self.footer)

    def internalImage(self):
        msg = "{{InternalImage|file={{#var:date}}_"+self.title.replace(" ", "_")+ self.count + "." + self.format + "}}\n"
        msg = replaceumlaut(msg)
        if self.type=="Podcast":
            msg = msg.replace("InternalImage","InternalImagePortrait")
        return(msg)
    def export_lesen(self):
        msg = self.date_string + "\t"  + self.start+"\t"+self.end+"\t"+self.page_start+"\t"+self.page_end+"\t"+self.title+"\n"
        path = 'generate/Reading_Times.txt'
        file_object = open(path, 'a')
        file_object.write(msg)
        file_object.close()

        #uniqueLines(path)


        return(msg)
    def upload_photo(self):
        #date_string = box.date.strftime("%Y-%m-%d")
        for box in self.box_array:
            box.upload_photo()
            # if box.media:
            #     if box.format !="jpg":
            #         return()
            #     img_name = box.date_string+"_"+box.title.replace(" ", "_")+ box.count + ".jpg"
            #     #print(img_name)
            #     #print("Upload: " + img_name)
            #     box.client.download_media(box.media,"./test.jpg")
            #     wiki = Wiki()
            #     #print("upload: " + img_name)
            #     wiki.upload_file("./test.jpg",img_name)
        if self.media:
            if self.noPhoto:
                return()
            if self.format !="jpg":
                return()
            img_name = self.date_string+"_"+self.title.replace(" ", "_")+ self.count + ".jpg"
            #print(img_name)
            #print("Upload: " + img_name)
            if type(self.message).__name__=="TelegramMessageJSON":
                self.message.download_media("./test.jpg")            
            else:
                self.client.download_media(self.media,"./test.jpg")
            wiki = Wiki()
            #print("upload: " + img_name)
            wiki.upload_file("./test.jpg",img_name)

    def generate_arbeit(self):
        #self.content = self.content + self.internalImage()
        message = self.header + self.content+ self.footer
        print(message)
        return message
    def generate_ausgabe_from_template(self):
        txt = Path('./templates/Ausgabe').read_text()
        txt = txt.replace("${Preis}",str(self.price))
        txt = txt.replace("${Laden}",self.laden)
        txt = txt.replace("${TAG}",self.tag)
        txt = txt.replace("${Source}",self.source)
        print(txt)
    def generate_einkauf(self):
        #self.content = self.content + self.internalImage()
        message = self.header + self.content+ self.footer
        print(message)
        return message
    def generate_einkauf_from_template(self):
        if len(self.box_array) > 0:
            for box in self.box_array:
                if self.ID != box.ID:
                    #print("Recursion " + self.title + "::" + box.title)
                    self.content = self.content + box.toString() + "\n"

        txt = Path('./templates/Einkauf').read_text()
        txt = txt.replace("${Preis}",str(self.price))
        txt = txt.replace("${Laden}",self.laden)
        txt = txt.replace("${TAG}",self.tag)
        txt = txt.replace("${Content}",self.content.strip())
        txt = txt.replace("${Source}",self.source)
        if(self.noPhoto):
            txt = txt.replace("{{InternalImage|file={{#var:date}}_{{#var:laden}}.jpg}}","")
            txt = txt.replace("{{InternalImage|file={{#var:date}}_{{#var:laden}}_Bon.jpg}}","")
        return(txt)
    def generate_event(self):
        self.content = self.content + self.internalImage()
        message = self.header + self.content+ self.footer
        print(message)
        return message
    def generate_gastro_from_template(self):
        if len(self.box_array) > 0:
            for box in self.box_array:
                if self.ID != box.ID:
                    #print("Recursion " + self.title + "::" + box.title)
                    try:
                        self.content = self.content + box.toString() + "\n"
                    except Exception as e:
                        print("Error: " + self.title)

        txt = Path('./templates/Gastro').read_text()
        txt = txt.replace("${Preis}",self.price)
        txt = txt.replace("${Laden}",self.laden)
        txt = txt.replace("${Content}",self.content.strip())
        txt = txt.replace("${Source}",self.source)
        #print(txt)
        return(txt)
    def generate_gedanken(self):
    	message = "{{Gedanken|title="+self.title+"|\n"+self.content+"}}"
    	#print(message)
    	return message
    
    def generate_general(self):
        #print(self.title + "::generate_kochen")
        if self.media and not self.noPhoto:
            self.content = self.content + self.internalImage()
        if self.precontent:
            self.content = self.precontent + self.content
        if len(self.box_array) > 0:
            for box in self.box_array:
                if self.ID != box.ID:
                    #print("Recursion " + self.title + "::" + box.title)
                    try:
                        self.content = self.content + box.toString() + "\n"
                    except Exception as e:
                        print("Error: " + self.title)

        message = self.header+self.content+"}}"
        #print(message)
        return message
    def generate_kochen(self):
        #print(self.title + "::generate_kochen")
        self.content = self.content + self.internalImage()
        if len(self.box_array) > 0:
            for box in self.box_array:
                if self.ID != box.ID:
                    print("Recursion " + self.title + "::" + box.title)
                    self.content = self.content + box.toString() + "\n"
        message = self.header+self.content+"}}"
        #print(message)
        return message
    def generate_lesen(self):
        self.content = self.precontent + self.content

        message = self.header+self.content+ self.footer
        print(message)
        return message
    def generate_meeting(self):
    	message = self.header+self.content+"}}"
    	print(message)
    	return message
    def generate_migraene(self):
        if self.media != "":
            self.content = self.internalImage() + self.content
        message = self.header+self.content+self.footer
        #print(message)
        return message
    def generate_photo(self):
        message=""
        if self.echo==True:
            message = self.internalImage()
            #print(message)
        #print(date)
        date_string = self.date.strftime("%Y-%m-%d")
        img_name = date_string + "_" +self.title.replace(" ", "_")+".jpg"
        #print(img_name)
        return message
    def generate_gallery(self):
        message=""
        date_string = self.date.strftime("%Y-%m-%d")
        img_name = date_string + "_" + "g-" +self.title.replace(" ", "_")+".jpg"
        #print(img_name)
        return message
    def generate_podcast(self):
        #print(self.media)
        if self.photo:
            img_name = self.date_string+"_"+self.title.replace(" ", "_")+ self.count + ".jpg"
            #print("Upload " + img_name)
            if self.media:
                self.client.download_media(self.media,"./test.jpg")
                wiki = Wiki()
                wiki.upload_file("./test.jpg",img_name)
                self.content = self.content + "{{InternalImagePortrait|file={{#var:date}}_"+self.title.replace(" ", "_")+self.count+".jpg}}\n"
        message = self.header +self.content+self.footer

        print(message)
        return message
    def generate_reise(self):
        if self.media != "":
            self.content = self.internalImage() + self.content
        message = self.header +self.content+ self.footer
        print(message)
        return message
    def generate_song(self):
        if self.media != "":
            self.content = self.internalImage() + self.content
        message = self.header+self.content+self.footer
        print(message)
        return message
    def generate_sport(self):
        if self.media != "":
            self.content = self.internalImage() + self.content
        message = self.header+self.content+self.footer
        print(message)
        return message
    def generate_spaziergang(self):
        if self.media != "":
            self.content = self.internalImage() + self.content
        self.content = self.content + self.internalImage()
        message = self.header+self.content+self.footer
        print(message)
        return message
    def generate_tag(self):
    	message = " |Has "+self.title + "\n"
    	#print(message)
    	return message
    def generate_video(self):
    	self.content = self.content +self.internalImage()
    	message = self.header+self.content+"}}"
    	print(message)
    	return message

    def get_time(self):
        return(self.time)


    def addBox(self,box):
        if not self.ID == box.ID and not box.inside=="" and not containsObject(box,self.box_array):
            #print("Add " + self.ID + " <- " + box.title)
            #self.box_array.append(box)
            self.box_array = self.box_array + [box]
            subset = self.box_array
            subset.sort(key=lambda x: x.time)
            subset = sorted(subset, key=lambda x: x.time)
            self.box_array = subset

            #print("Now" + self.ID)
            #for b in self.box_array:
            #    print("= " + b.title)
#box =  DiaryBox("Podcast")


class DiarySet:
    boxes = []
    tags = []

    def __init__(self):
        self.boxes = []
        self.tags = []

    def create_from_array(self,box_array):
        for box in box_array:
            if box.type!="Tag":
                self.boxes.append(box)
                #if(len(box.box_array)>0):
                #    self.create_from_array(box.box_array)
    def tags_from_array(self,box_array):
        for box in box_array:
            if box.type=="Tag":
                self.tags.append(box)
            else:
                self.tags.append(box.tags_toString())
                if(len(box.box_array)>0):
                    self.tags_from_array(box.box_array)
        #print("Diaryset::" + self.tags_toString())

    def tags_toString(self):
        txt = ""
        for tag in self.tags:
            if type(tag) is str:
                txt = txt + tag
            else:
                txt = txt + tag.toString()
        return(txt)
