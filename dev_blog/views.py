from django.shortcuts import render, redirect
from django.http import HttpResponse
import os
from CRUD import CRUD
import hashlib
import time
import ast
from datetime import datetime
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Article


import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# Add these views to your views.py file
class ArticleCreateView(CreateView):
    model = Article
    fields = ['title', 'content']
    template_name = 'article_form.html'
    success_url = reverse_lazy('home')  # or wherever you want to redirect after creation

class ArticleUpdateView(UpdateView):
    model = Article
    fields = ['title', 'content']
    template_name = 'article_form.html'
    success_url = reverse_lazy('home')



db = CRUD()

@csrf_exempt
def upload_media(request):
    if request.method == 'POST' and request.FILES.get('upload'):
        upload = request.FILES['upload']
        
        # Get file extension to determine type
        filename = upload.name.lower()
        ext = filename.split('.')[-1] if '.' in filename else ''
        
        # Define allowed extensions
        allowed_video_extensions = ['webm', 'mp4', 'ogg', 'avi', 'mov']
        allowed_image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']
        
        # Check if extension is allowed
        if not (ext in allowed_video_extensions or ext in allowed_image_extensions):
            return JsonResponse({
                'uploaded': False,
                'error': f'File extension not allowed: .{ext}. Supported: {", ".join(allowed_video_extensions + allowed_image_extensions)}'
            }, status=400)
        
        try:
            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}.{ext}"
            
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join('uploads', unique_filename)
            path = default_storage.save(file_path, ContentFile(upload.read()))
            
            # Return URL
            url = request.build_absolute_uri(settings.MEDIA_URL + path)
            
            return JsonResponse({
                'uploaded': True,
                'url': url,
                'filename': unique_filename,
                'is_video': ext in allowed_video_extensions
            })
            
        except Exception as e:
            return JsonResponse({
                'uploaded': False,
                'error': f'Upload failed: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'uploaded': False,
        'error': 'Invalid request - no file uploaded'
    }, status=400)

### GET
### TEMPLATE ENDPOINTS
###
def home(request):
    if isSession(request) and not db.isSessionValid(request): return logout(request)
    pageFile = os.path.join("pages", "home.html")
    return render(request, pageFile)


def changelogSite(request):
    if isSession(request) and not db.isSessionValid(request): return logout(request)
    pageFile = os.path.join("pages", "changelog.html")
    allChangelogs = db.read("changelogs", "logs")
    logs = []
    for item in allChangelogs:
        logs.append({
            "id": item[3],  # DB ID
            "title": item[1],
            "date": item[0],
            "parsed_date": datetime.strptime(item[0], "%d.%m.%Y"),
            "changes": str(item[2]),
        })

    logs.sort(key=lambda x: x["parsed_date"], reverse=True)
    for log in logs:
        del log["parsed_date"]
    context = {"logs": logs}
    return render(request, pageFile, context)


### POST
### LOGIN / LOGOUT ENDPOINTS
###
def login(request):
    if request.method == "POST":
        print("login request received")
        submitted_data = request.POST
        enteredUsername, enteredPassword = submitted_data["username"], submitted_data["password"]
        enteredHash = db.generateHash(enteredUsername, enteredPassword)

        if db.areCredsValid(enteredHash):
            sessionToken = db.generateSessionToken()
            db.create("sessions", "sessions", (str(enteredHash), str(sessionToken), int(time.time())))    
            print(f"logged in user: {enteredUsername}")             
            return appendUserDataToResponse(redirect("/home"), enteredUsername, enteredHash, sessionToken)
    return redirect("/home")

def logout(request):
    userCookies = request.COOKIES
    db.delete("sessions", "sessions", "id", userCookies.get("ID", ""))
    print("logged out user: " + userCookies.get("USERNAME"))
    return wipeUserCookies(redirect("/home"))

### POST
### FUNCTIONAL ENDPOINTS
###
def addNewChangelogEntry(request):
    if isSession(request) and request.method == "POST":
        if db.isSessionValid(request):
            submitted_data = request.POST
            correctedDate = ".".join(submitted_data['date'].replace("-", ".").split(".")[::-1])
            # Use 'content' instead of 'changes'
            content = submitted_data.get('content', '')
            print(content)
            db.create("changelogs", "logs", (correctedDate, str(submitted_data['title']), content), ("Date", "Title", "Changes"))
            print(f"user {request.COOKIES.get('USERNAME')} CREATED new changelog entry; title: {str(submitted_data['title'])}\ndate: {correctedDate}")
            return redirect("/changelog")
        else: 
            return wipeUserCookies(redirect("/home"))
    return redirect("/home")

def removeChangelogEntry(request):
    if isSession(request) and request.method == "POST":
        if db.isSessionValid(request):
            db.delete("changelogs", "logs", "ID", request.POST["changeID"])
            print(f"user {request.COOKIES.get('USERNAME')} DELETED changelog entry; ID: {request.POST["changeID"]}")
        else: return logout(request)
    return redirect("/changelog")

def editChangelogEntry(request):
    if isSession(request) and request.method == "POST":
        if db.isSessionValid(request):
            submitted_data = request.POST
            correctedDate = ".".join(submitted_data['date'].replace("-", ".").split(".")[::-1])
            # Use 'content' instead of the list of changes
            content = submitted_data.get('content', '')
            values = [correctedDate, submitted_data['title'], content]
            db.update(database="changelogs", table="logs", columns=["Date", "Title", "Changes"], whereColumn="ID", whereValue=submitted_data["dbid"], values=values)
            print(f"user {request.COOKIES.get('USERNAME')} EDITED changelog entry; new title: {submitted_data['title']}\nnew date: {correctedDate}")
        else: 
            return logout(request)
    return redirect("/changelog")


###
### HELPER FUNCTIONS
###
def isSession(request):
    if request.COOKIES.get("ID") and request.COOKIES.get("SESH_TOKEN") and request.COOKIES.get("USERNAME"):
        return True
    else: return False

def appendUserDataToResponse(response, username, checksum, sessionToken):
      response.set_cookie("USERNAME", str(username))
      response.set_cookie("ID", str(checksum))
      response.set_cookie("SESH_TOKEN", str(sessionToken))
      return response

def wipeUserCookies(response):
    response.delete_cookie("USERNAME")
    response.delete_cookie("ID")
    response.delete_cookie("SESH_TOKEN")
    return response