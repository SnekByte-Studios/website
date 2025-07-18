from django.shortcuts import render, redirect
from django.http import HttpResponse
import os
from CRUD import CRUD
import hashlib
import time
import ast
from datetime import datetime

db = CRUD()

def home(request):
    pageFile = os.path.join("pages", "home.html")
    return render(request, pageFile)


def changelogSite(request):
    pageFile = os.path.join("pages", "changelog.html")
    allChangelogs = db.read("changelogs", "logs")  # List of tuples
    print("CHANGELOGS: ")
    print(allChangelogs)

    # Convert to list of dicts and parse the date
    logs = []
    for item in allChangelogs:
        logs.append({
            "id": item[3],  # DB ID
            "title": item[1],
            "date": item[0],
            "parsed_date": "", #datetime.strptime(item[0], "%d.%m.%Y"),
            "changes": ast.literal_eval(item[2]),
        })

    # Sort logs by parsed date descending
    logs.sort(key=lambda x: x["parsed_date"], reverse=True)

    # Remove parsed_date before sending to template if you don't need it there
    for log in logs:
        del log["parsed_date"]

    # Send sorted logs to template
    context = {"logs": logs}
    return render(request, pageFile, context)

def login(request):
    if request.method == "POST":
        submitted_data = request.POST
        enteredUsername, enteredPassword = submitted_data["username"], submitted_data["password"]
        enteredHash = db.generateHash(enteredUsername, enteredPassword)
        if db.areCredsValid(enteredHash):
            sessionToken = db.generateSessionToken()
            db.create("sessions", "sessions", (str(enteredHash), str(sessionToken), int(time.time())))                 
            return appendUserDataToResponse(redirect("/home"), enteredUsername, enteredHash, sessionToken)
    return redirect("/home")

def logout(request):
    userCookies = request.COOKIES
    print("logging out ...")
    db.delete("sessions", "sessions", "id", userCookies.get("ID", ""))
    return wipeUserCookies(redirect("/home"))

def addNewChangelogEntry(request):
    if request.method == "POST":
        if db.isSessionValid(request):
            submitted_data = request.POST
            correctedDate = ".".join(submitted_data['date'].replace("-", ".").split(".")[::-1])
            db.create("changelogs", "logs", (correctedDate, str(submitted_data['title']), str(submitted_data.getlist('changes'))), ("Date", "Title", "Changes"))
            return redirect("/changelog")
        else: return wipeUserCookies(redirect("/home"))      

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

def removeChangelogEntry(request):
    if request.method == "POST":
        if db.isSessionValid(request):
            db.delete("changelogs", "logs", "ID", request.POST["changeID"])
        else: logout(request)
    return redirect("/changelog")

def editChangelogEntry(request):
    if request.method == "POST" and db.isSessionValid(request):
        submitted_data = request.POST
        correctedDate = ".".join(submitted_data['date'].replace("-", ".").split(".")[::-1])
        values = [correctedDate, submitted_data['title'], str(submitted_data.getlist('changes'))]
        db.update(database="changelogs", table="logs", columns=submitted_data.getlist("columns"), whereColumn="ID", whereValue=submitted_data["dbid"], values=values)
    else: logout(request)
    return redirect("/changelog")
