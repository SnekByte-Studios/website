from django.shortcuts import render, redirect
from django.http import HttpResponse
import os
from CRUD import CRUD
import hashlib
import time
import ast
from datetime import datetime

db = CRUD()


### GET
### TEMPLATE ENDPOINTS
###
def home(request):
    if isSession(request) and not db.isSessionValid(request): logout(request)
    pageFile = os.path.join("pages", "home.html")
    return render(request, pageFile)


def changelogSite(request):
    if isSession(request) and not db.isSessionValid(request): logout(request)
    pageFile = os.path.join("pages", "changelog.html")
    allChangelogs = db.read("changelogs", "logs")
    logs = []
    for item in allChangelogs:
        logs.append({
            "id": item[3],  # DB ID
            "title": item[1],
            "date": item[0],
            "parsed_date": datetime.strptime(item[0], "%d.%m.%Y"),
            "changes": ast.literal_eval(item[2]),
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
            db.create("changelogs", "logs", (correctedDate, str(submitted_data['title']), str(submitted_data.getlist('changes'))), ("Date", "Title", "Changes"))
            print(f"user {request.COOKIES.get('USERNAME')} CREATED new changelog entry; title: {str(submitted_data['title'])}\ndate: {correctedDate}")
            return redirect("/changelog")
        else: return wipeUserCookies(redirect("/home"))
    return redirect("/home")

def removeChangelogEntry(request):
    if isSession(request) and request.method == "POST":
        if db.isSessionValid(request):
            db.delete("changelogs", "logs", "ID", request.POST["changeID"])
            print(f"user {request.COOKIES.get('USERNAME')} DELETED changelog entry; ID: {request.POST["changeID"]}")
        else: logout(request)
    return redirect("/changelog")

def editChangelogEntry(request):
    if isSession(request) and request.method == "POST":
        if db.isSessionValid(request):
            submitted_data = request.POST
            correctedDate = ".".join(submitted_data['date'].replace("-", ".").split(".")[::-1])
            values = [correctedDate, submitted_data['title'], str(submitted_data.getlist('changes'))]
            db.update(database="changelogs", table="logs", columns=submitted_data.getlist("columns"), whereColumn="ID", whereValue=submitted_data["dbid"], values=values)
            print(f"user {request.COOKIES.get('USERNAME')} EDITED changelog entry; new title: {submitted_data['title']}\nnew date: {correctedDate}")
        else: logout(request)
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