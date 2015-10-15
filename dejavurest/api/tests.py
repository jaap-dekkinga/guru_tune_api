from django.test import TestCase
import requests
import MySQLdb
import os
#import pygame


DEJAVU_DATABASE = 'dejavu'
DEJAVU_DBUSER = 'dejavu'
DEJAVU_DBPASS = 'dejavu123'
DEJAVU_DBHOST = "localhost"

CREATE_RECORD_URL = "http://52.89.0.191:8000/api/add_record"  
VERIFY_RECORD_URL = "http://52.89.0.191:8000/api/match"  



class DejavuAPITestCase(TestCase):
    def setUp(self):
        self.config = {
            "database": {
                "host": DEJAVU_DBHOST,
                "user": DEJAVU_DBUSER,
                "passwd": DEJAVU_DBPASS,
                "db": DEJAVU_DATABASE,
            }
        }

        
def test_fingerprinting():
    """
    print "Flushing existing records..."

    db = MySQLdb.connect(DEJAVU_DBHOST, DEJAVU_DBUSER, DEJAVU_DBPASS, DEJAVU_DATABASE)
    cursor = db.cursor()
    cursor.execute("set autocommit = 1")
    query = "delete from fingerprints"
    cursor.execute(query)
    result = cursor.fetchone()
    print result
    query = "delete from songs"
    cursor.execute(query)
    result = cursor.fetchone()
    print result
    print "Flushed existing records..."
    cursor.close()
    db.close()
    """
    
    print "Creating new records through API"
    record_directory = "/home/murthyraju/Documents/fl/dejavu/samples_archive/Carnatic_short"
    files = os.listdir(record_directory)
    counter = 1
    for f in files:
        if "mp3" in f:
            file_path = os.path.join(record_directory, f)
            uploadable_files = {'file': open(file_path, 'rb')}
            print "%d" %(counter) 
            print 24 * "---"
            print "Uploading %s" % (file_path)
            r = requests.post(CREATE_RECORD_URL, files=uploadable_files)
            print "Response from the server: " + r.text
            print 24 * "---"
            print "\n"
            counter += 1
    print "Done fingerprinting"
 
    
    print "Verifying through API"
    record_directory = "/home/murthyraju/Documents/fl/dejavu/samples_archive/Carnatic_shorter"
    files = os.listdir(record_directory)
    counter = 1
    correct_match = 1
    for f in files:
        if "mp3" in f:
            file_path = os.path.join(record_directory, f)
            song_name = f[8:-4]
            uploadable_files = {'file': open(file_path, 'rb')}
            print "%d" %(counter) 
            print 24 * "---"
            print "Uploading for verification %s" % (file_path)
            r = requests.post(VERIFY_RECORD_URL, files=uploadable_files)
            #print type(eval(r.text))
            #print eval(r.text)
            returned_song_name = eval(r.text)["song_name"][6:]
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