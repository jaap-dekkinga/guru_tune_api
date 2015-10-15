#from django.test import TestCase
import requests
#import MySQLdb
import os
#import pygame


DEJAVU_DATABASE = 'dejavu'
DEJAVU_DBUSER = 'dejavu'
DEJAVU_DBPASS = 'dejavu123'
DEJAVU_DBHOST = "localhost"

#CREATE_RECORD_URL = "http://52.89.0.191:8000/api/add_record"  
#VERIFY_RECORD_URL = "http://52.89.0.191:8000/api/match"  

CREATE_RECORD_URL = "http://localhost:8000/api/add_record"  
VERIFY_RECORD_URL = "http://localhost:8000/api/match"
CLEANUP_URL =  "http://localhost:8000/api/song_repo" 
       
def test_fingerprinting():
    
    print "Flushing existing records..."
    r = requests.delete(CLEANUP_URL)
    print "Response from the server: " + r.text
    print "Flushed existing records..."
    
    
    """
    URL: http://52.89.0.191:8000/api/add_record
    METHOD: POST
    Headers: "Content-Type: multipart/form-data"
    DATA:
    file="@/home/murthyraju/Documents/fl/dejavu/code/samples/short/short_opor_-_08_-_Svi_Gradovi.mp3"
    title=Svi Gradovi Song in MP3 format
    description = "A great Song. You must listen to this song"
    url = "http://www.google.com/"
    curl -X POST -H "Content-Type: multipart/form-data" -F "file=@/home/murthyraju/Documents/fl/dejavu/code/samples/short/short_opor_-_08_-_Svi_Gradovi.mp3" -F "title=Svi Gradovi Song in MP3 format" -F "description=A very nice song. Must listen" -F "url=http://www.google.com/Svi_Gradovi.mp3" 
    
    """

    print "Creating new records through API"
    record_directory = "/home/murthyraju/Documents/fl/dejavu/samples_archive/Carnatic_short"
    files = os.listdir(record_directory)
    counter = 1
    for f in files:
        if "mp3" in f:
            file_path = os.path.join(record_directory, f)
            uploadable_files = {'file': open(file_path, 'rb')}
            
            file_name_plus_ext = os.path.basename(file_path)
            file_name = os.path.splitext(file_name_plus_ext)[0]
            title = "Nice Song - %s" % ( file_name )
            description = "Nice Song Described here -- %s" % ( file_name )
            url = "http://www.google.com/songs/%s%s" % ( file_name, ".mp3")
            data = {'title':title, 'description': description, 'url': url}
            
            print "%d" %(counter) 
            print 24 * "---"
            print "Uploading %s" % (file_path)
            r = requests.post(CREATE_RECORD_URL, files=uploadable_files, data=data)
            print "Response from the server: " + r.text
            print 24 * "---"
            print "\n"
            counter += 1
    print "Done fingerprinting"

    
    print "Verifying through API"
    record_directory = "/home/murthyraju/Documents/fl/dejavu/samples_archive/Carnatic_shorter"
    files = os.listdir(record_directory)
    counter = 0
    correct_match = 0
    for f in files:
        if "mp3" in f:
            file_path = os.path.join(record_directory, f)
            song_name = f[8:-4]
            uploadable_files = {'file': open(file_path, 'rb')}
            print "%d" %(counter) 
            print 24 * "---"
            print "Uploading for verification %s" % (file_path)
            r = requests.post(VERIFY_RECORD_URL, files=uploadable_files)
            print type(eval(r.text))
            print eval(r.text)
            returned_song_name = eval(r.text)["data"]["song_name"][6:]
            print "Response from the server: " + r.text
            print "\n"
            if song_name == returned_song_name:
                correct_match += 1
            print "%s --- %s" % (song_name, returned_song_name) 
            print 24 * "---"
            print "\n"
            counter += 1
    print "Done verifying. Match Efficiency: %d / %d" % (correct_match, counter )    
    
    print "Verifying songs with background noise through API"
    record_directory = "/home/murthyraju/Documents/fl/dejavu/samples_archive/Carnatic_recorded"
    files = os.listdir(record_directory)
    counter = 0
    correct_match = 0
    for f in files:
        if "mp3" in f:
            file_path = os.path.join(record_directory, f)
            song_name = f[17:-4]
            uploadable_files = {'file': open(file_path, 'rb')}
            print "%d" %(counter) 
            print 24 * "---"
            print "Uploading for verification %s" % (file_path)
            r = requests.post(VERIFY_RECORD_URL, files=uploadable_files)
            print type(eval(r.text))
            print eval(r.text)
            returned_song_name = eval(r.text)["data"]["song_name"][6:]
            print "Response from the server: " + r.text
            print "\n"
            if song_name == returned_song_name:
                correct_match += 1
            print "%s --- %s" % (song_name, returned_song_name) 
            print 24 * "---"
            print "\n"
            counter += 1
    print "Done verifying. Match Efficiency: %d / %d" % (correct_match, counter )  
    
    """
    print "Verifying By Playing/Recording/Uploading."
    record_directory = "/home/murthyraju/Documents/fl/dejavu/samples_archive/Carnatic_shorter"
    files = os.listdir(record_directory)
    counter = 1
    correct_match = 1
    for f in files:
        if "mp3" in f:           
            file_path = os.path.join(record_directory, f)
            print "Playing " + file_path
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy() == True:
                continue
            print "Done playing " +  file_path 
            counter += 1
    #print "Done verifying. Match Efficiency: %d / %d" % (correct_match, counter )   
    """
        
#testcase = DejavuAPITestCase()
print "About to run tests..."
test_fingerprinting()
