from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from rest_framework import status
from collections import OrderedDict
import urllib
import math
import pdb
from django.conf import settings
import os

from api.models import SongDetail

import MySQLdb
from dejavu import Dejavu
from dejavu.recognize import FileRecognizer
from api.models import *
        
# Create your views here.
#http://stackoverflow.com/questions/16571150/how-to-capture-stdout-output-from-a-python-function-call
from cStringIO import StringIO
import sys


class Capturing(list):
    """
    Context Manager to capture stdout that we get from Dejavu Library Calls
    dejavu methods such as fingerprint_file do not return anything and we can 
    get information about the result by reading the stdout    
    """
    
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout

def enhance_song_data(song_dict, song_detail):
    """
    Dejavu captures certain details about each song, such as name.
    We capture additional details and this function is called to populate the 
    song dict with these additional details such as title, description, url
    """
    
    if hasattr(song_detail, "title") and \
            song_detail.title is not None and \
            len(song_detail.title.strip()) > 0:
        song_dict["title"] = song_detail.title
        
    if hasattr(song_detail, "description") and \
            song_detail.description is not None and \
            len(song_detail.description.strip()) > 0:
        song_dict["description"] = song_detail.description

    if hasattr(song_detail, "url") and \
            song_detail.url is not None and \
            len(song_detail.url.strip()) > 0:
        song_dict["url"] = song_detail.url
    
    if hasattr(song_detail, "creation_time") and \
            song_detail.creation_time is not None:
        song_dict["creation_time"] = song_detail.creation_time

    if hasattr(song_detail, "modification_time") and \
            song_detail.modification_time is not None:
        song_dict["modification_time"] = song_detail.modification_time

    return song_dict


class DBCleanupView(APIView):
    def post(self, request):
        return Response({"status":"Not Implemented"})

    def put(self, request):
        return Response({"status":"Not Implemented"})

    def get(self, request):
        return Response({"status": "Not Implemented"})  
    
    def delete(self, request):
        result = {}
        deletion_error = False
        
        try:
            db = MySQLdb.connect(settings.DEJAVU_CONFIG["database"]["host"],
                                 settings.DEJAVU_CONFIG["database"]["user"],
                                 settings.DEJAVU_CONFIG["database"]["passwd"],
                                 settings.DEJAVU_CONFIG["database"]["db"])        
            sql = "DELETE from fingerprints"
            cursor = db.cursor()
            cursor.execute(sql)
            fingerprint_deletion_result = cursor.fetchone()
            db.commit()
            
            sql = "DELETE from songs"
            cursor.execute(sql)
            song_deletion_result = cursor.fetchone()
            db.commit()
            
            result["status"] = "Deleted Successfully"            
        except:            
            result["status"] = "Failed to delete"
            deletion_error = True
            
        if not deletion_error:
            try:
                SongDetail.objects.all().delete()
            except:
                result["status"] += " Failed to delete song detail data"
                deletion_error = True
                
        if not deletion_error:
            return Response({"data" : result}) 
        else:
            return Response({"data" : result}, status.HTTP_500_INTERNAL_SERVER_ERROR)

class RecordUploadView(APIView):
    parser_classes = (FileUploadParser,)

    def post(self, request, format='mp3'):
        """
        Called to fingerprint an mp3 file. 
        Dejavu stores the song details along with fingerprints.
        We store additional details such as title,description, url in a custom
        mysql table through Django ORM
        """
        result = {}
        
        # Store the uploaded file in a temporary location.
        # If no file uploaded or any other error. Return an error
        file_upload_error = False
        try:
            up_file = request.FILES['file']
            if not os.path.isdir(settings.DEJAVU_UPLOADED_FILES_TEMP):
                os.mkdir(settings.DEJAVU_UPLOADED_FILES_TEMP)
            target_file_name = os.path.join(settings.DEJAVU_UPLOADED_FILES_TEMP, up_file.name)
            song_name, ext = os.path.splitext(up_file.name)
            with open(target_file_name, 'wb+') as destination:
                for chunk in up_file.chunks():
                    destination.write(chunk)
        except:
            file_upload_error = True
            success = False
            result["status"] = "File Upload Error"        


        if not file_upload_error:
            # Fingerprinting
            print "starting to finger print"
                    
            try:
                djv = Dejavu(settings.DEJAVU_CONFIG)        
                with Capturing() as output:    
                    djv.fingerprint_file(target_file_name, [song_name])
                output_string = "\n".join(output)
                
                print "Output from dejavu: " + output_string
                
                # Dejavu is minimal in its feedback.If already recorded
                # dejavu just prints to stdout that it is 'already fingerprinted'
                # We find out the song on record by calling 'recognize' method
                
                # If successfully fingerprinted,we do a recognize to fetch the details
                # such as song_id as dejavu does not provide it.
                # We store additional details - title, description, url 
                # in custom Django model
                
                if "already fingerprinted" in output_string:
                    song = djv.recognize(FileRecognizer, target_file_name)
                    result["status"] = "Already fingerprinted. So skipped!"
                    try:
                        song_detail = SongDetail.objects.get(song_id=song["song_id"])
                        song = enhance_song_data(song, song_detail)
                    except:
                        print "Error fetching song detail object"
                    result["song"] = song                
                    success = True
                elif "Fingerprinting channel" in output_string and \
                    "Finished channel" in output_string:
                    song = djv.recognize(FileRecognizer, target_file_name)                               
                    try:
                        song_detail = SongDetail()
                        song_detail.song_id=song["song_id"]
                        if request.POST.get("title"):
                            song_detail.title = request.POST.get("title")
                        if request.POST.get("description"):
                            song_detail.description = request.POST.get("description")
                        if request.POST.get("url"):                    
                            song_detail.url = request.POST.get("url")
                        song_detail.save()
                        song = enhance_song_data(song, song_detail)
                    except:
                        print "Error fetching song detail object"                   
                    result["song"] = song   
                    result["status"] = "Finger printed and stored with song_id " + str(song["song_id"])
                    success = True
                else:
                    result["status"] = "Unknown Error. Failed to fingerprint"
                    success = False
            except:
                success = False
                result["status"] = "Unknown Exception occured. Failed to fingerprint"            
            
            try: 
                # Remove the tempfile   
                os.remove(target_file_name)
            except:
                pass
        
        if success:
            return Response({"data" : result}, status.HTTP_201_CREATED)
        else:
            return Response({"data" : result}, status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListObjects(APIView):
    """
    View to list all objects
    """
    def fetch_elements(self, page_number=1, page_size=10):

        
        # dejavu does not provide a method to list the songs
        # We connect to the databse of dejavu and compute the list
        # and use Django ORM to fetch additional song details.
        
        print "page_number: " + str(page_number)
        
        db = MySQLdb.connect(settings.DEJAVU_CONFIG["database"]["host"],
                             settings.DEJAVU_CONFIG["database"]["user"],
                             settings.DEJAVU_CONFIG["database"]["passwd"],
                             settings.DEJAVU_CONFIG["database"]["db"])
        
        start = (page_number - 1) * page_size

        cursor = db.cursor()
        sql = "SELECT * from songs"
        cursor.execute(sql)
        row_count = cursor.rowcount
        print "Total Rows: " + str(row_count)

        sql = "SELECT song_id, song_name FROM songs LIMIT " + str(page_size) + " OFFSET " + str(start)
        print sql
        songs = []
        try:
            # Execute the SQL command
            cursor.execute(sql)
            # Fetch all the rows in a list of lists.
            results = cursor.fetchall()
            for row in results:
                song = {}
                song["song_id"] = row[0]
                song["name"] = row[1]                
                try:
                    song_detail = SongDetail.objects.get(song_id=song["song_id"])
                    song = enhance_song_data(song, song_detail)
                except:
                    pass
                songs.append(song)
                print "song_name=%s" % (song["name"],)
        except:
            print "Error: unable to fetch data"

        db.close()
        return row_count, songs

    def get_count(self):
        return 50

    def get(self, request):
        """
        Provides a paginated list of objects. 
        page_number and page_size can be provided as 
        GET params while making the call.
        metadata section is useful if you are using this an app and want to 
        create next_page, prev_page links etc.
        """
        page_number = int(request.GET.get("page_number") or 1)
        page_size = int(request.GET.get("page_size") or 10)
        total_count, elements = self.fetch_elements(page_number=page_number,
            page_size=page_size)
        
        total_pages = int(math.ceil(float(total_count) / page_size))
        next_page = page_number + 1 if page_number < total_pages else None
        previous_page = page_number - 1 if page_number - 1 <= 1 else None

        response = {}
        metadata = OrderedDict() 
        metadata["Total Count"] = total_count
        metadata["Total Pages"] = total_pages
        
        metadata["Current Page"] = "/api/list?" + \
            urllib.urlencode({"page_number":page_number,
                "page_size":page_size})
            
        if previous_page:
            metadata["Previous Page"] = "/api/list?" + \
                urllib.urlencode({"page_number":previous_page,
                    "page_size":page_size})
                
        if next_page:
            metadata["Next Page"] = "/api/list?" + \
                urllib.urlencode({"page_number":next_page,
                    "page_size":page_size})

        
        metadata["First Page"] = "/api/list?" + \
            urllib.urlencode({"page_number":1, "page_size":page_size})

        metadata["Last Page"] = "/api/list?" + \
            urllib.urlencode({"page_number":total_pages,
                "page_size":page_size})

        response_dict = {"metadata":metadata,
            "data":elements
        }
            
        return Response(response_dict)

    def post(self, request):
        """
        doc string
        """
        return Response({"status":"Not Implemented"})

    def put(self, request):
        """
        doc string
        """
        return Response({"status":"Not Implemented"})

    def delete(self, request):
        """
        doc string
        """
        return Response({"status": "Not Implemented"})


class VerifyObject(APIView):
    parser_classes = (FileUploadParser,)

    def get(self, request):
        return Response({"status":"Not Implemented"})
    
    def delete(self, request):
        return Response({"status": "Not Implemented"})

    def put(self, request, format='mp3'):
        return Response({"status": "Not Implemented"})

    def post(self, request):
        result = {}
        parser_classes = (FileUploadParser,)
        try:
            up_file = request.FILES['file']
        except:
            print type(request.data)
            up_file = request.data['file']
        target_file_name = os.path.join(settings.DEJAVU_UPLOADED_FILES_TEMP, up_file.name)
        destination = open(target_file_name, 'wb+')
        
        for chunk in up_file.chunks():
            destination.write(chunk)
            destination.close()
        
        djv = Dejavu(settings.DEJAVU_CONFIG) 
        print "starting to recognize"
        song = djv.recognize(FileRecognizer, target_file_name)
        if song is not None:
            song_detail = SongDetail.objects.get(song_id=song["song_id"])
            song = enhance_song_data(song, song_detail)
            result["song"] = song
            result["status"] = "Match Found"
        else:
            result["status"] = "No Match"
            
        print "Done recognizing"
        
        try: 
            # Remove the tempfile   
            os.remove(target_file_name)
        except:
            pass
                
        if song is not None:
            result = song
        else:
            result["status"] = "No Match"
        destination.close()
        return Response({"data":result})
      
