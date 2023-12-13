# YourPhotoHost (YPH)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-%3E%3D3.6-blue.svg)](https://www.python.org/downloads/)

## Overview
YourPhotoHost (YPH) is a web application that allows users to upload, view, and manage their images online. Users can create an account, upload images, and organize them into different categories. They can also like, favorite and report images, as well as leave comments on images uploaded by others.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Screenshots](#screenshots)

  
## Installation

A. To set up the YourPhotoHost application locally, follow these steps:

1. Clone the repository:
```
git clone https://github.com/MurtadaAhmed/YPH-YourPhotoHost.git
cd YPH-YourPhotoHost
cd murtidjango
```

2. Create a virtual environment and activate it (optional but recommended):
```
python -m venv venv
source venv/bin/activate # On Windows, use venv\Scripts\activate
```

3. Install the required dependencies:
```
pip install -r requirements.txt
```
4. Set up the database:
```
python manage.py makemigrations
python manage.py migrate
```
5. Create a superuser (admin) account:
```
python manage.py createsuperuser
```

7. Run the development server:
```
python manage.py runserver
```

YourPhotoHost should now be accessible at `http://localhost:8000/`.

B. To deploy the app on Windows Server 2022 (IIS + HttpPlatform handler):
1. Download the project files and extract them:
c:/projectfolder/manage.py

2. Download Python:
https://www.python.org/downloads

3. Setup the requirements:
Open CMD in the folder c:/projectfolder/ and run:
```
pip install -r requirements.txt
```

4. From the server manager >> Add roles and features >> IIS

5. Download and install HttpPlatformHandler:
https://www.iis.net/downloads/microsoft/httpplatformhandler

6. From the Server Manager > Tools > IIS Manager > Choose your server > Under 'Management' section select: Feature Delegation > Handler Mappings > Select Read/Write (from the right side)

7. From the Server Manager > Tools > IIS Manager > Choose your server > Sites > Add website:

Site name: mywebsite.com

Physical path: c:/projectfolder/

Binding: select the local ip address

Ok

9. From the Server Manager > Tools > IIS Manager > Choose your server > Sites > mywebsite.com > Under 'Management' select 'Configuration Editor' > from the 'Section' drop down menu select system.webServer >> httpPlatform:

arguments: C:\projectfolder\manage.py runserver %HTTP_PLATFORM_PORT%

environmentVariables: click on the (...) > Add:

  name: SERVER_PORT
  value: %HTTP_PLATFORM_PORT%
  
processPath: path where “python.exe” is. For example: C:\Python312\python.exe

stdoutLogEnabled: True

stdoutLogFile: the path where to store the log file. For example: C:\projectfolder\logs\logs.log

After entering these information, click on 'Apply' on the upper right side.

10. From the Server Manager > Tools > IIS Manager > Choose your server > Sites > mywebsite.com > Under 'Management' select 'Configuration Editor' > from the 'Section' drop down menu select 'appSettings' > click on the (...):
    
Add: 
  key: PYTHONPATH
  value: C:\projectfolder
  
Add:
  key: WSGI_HANDLER
  value: django.core.wsgi.get_wsgi_application()
  
Add:
  key: DJANGO_SETTINGS_MODULE
  value: murtidjango.settings (for example if the project folder that has the settins.py is called "murtidjango" in C:\projectfolder\murtidjango)
  
After entering these information and closing this window, click on 'Apply' on the upper right side on the previous window.

12. From the Server Manager > Tools > IIS Manager > Choose your server > Sites > mywebsite.com > Under 'ISS' section select 'Handler Mappings' > Add Module Mapping (from the right side):
    
    Request path: *
    
    Module: httpPlatformHandler
    
    Name: MyPyHandler

    Then click on “Request Restrictions” > untick the option “Invoked handler only if requests is mapped to” > OK > OK

After doing these steps, the website should be accessible using your ip.
To confirm that the correct settings are applied, check the web.config file here: C:\projectfolder\web.config. The contents should look like this:
```
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <httpPlatform processPath="C:\Python312\python.exe" arguments="C:\projectfolder\manage.py runserver %HTTP_PLATFORM_PORT%" stdoutLogEnabled="true" stdoutLogFile="C:\projectfolder\logs\logs.log">
            <environmentVariables>
                <environmentVariable name="SERVER_PORT" value="%HTTP_PLATFORM_PORT%" />
            </environmentVariables>
        </httpPlatform>
        <handlers>
            <add name="MyPyHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified" />
        </handlers>
    </system.webServer>
    <appSettings>
        <add key="PYTHONPATH" value="C:\projectfolder" />
        <add key="WSGI_HANDLER" value="django.core.wsgi.get_wsgi_application()" />
        <add key="DJANGO_SETTINGS_MODULE" value="murtidjango.settings" />
    </appSettings>
</configuration>
```
    
**Important:** make sure to change the database information (host, database name, username, password then: python manage.py makemigrations & python manage.py migrate & python manage.py createsuperuser) and the email server settings in settings.py


## Usage
1. Navigate to the application URL and sign up for a new account or log in if you already have one.

2. Once logged in, you can upload images by clicking on the "Upload New Image" button.

3. Manage your images in the "My Images" section, where you can view, edit, delete, and organize them into categories.

4. Explore other users' images and interact with them by liking, favoriting, and leaving comments.

## Features
- User authentication and account management
- Image upload from computer or from URL.
- Sinlge/Multiple images upload
- Managing uploaded images (resize/rename/private or public/delete)
- Categorization of images
- Albums creation
- Like or unlike functionality
- Favorite or unfavorite functionality
- Commenting on images
- Report Images
- Moderators with special privileges for image moderation

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
Special thanks to [Software University](https://softuni.bg/) team and their amazing teachers.

## Screenshots:

**Guests homepage view:**

<img src="https://github.com/MurtadaAhmed/YPH-YourPhotoHost/assets/108568451/893fc06c-7466-476e-9fea-8f13a3543e6d" alt="Guests homepage view" width="500">  

***************************

**Authenticated users homepage view:**

<img src="https://github.com/MurtadaAhmed/YPH-YourPhotoHost/assets/108568451/d1503fe0-c425-4ef2-b880-fa8822786b40" alt="Authenticated users homepage view" width="500"> 

***************************

**Image view:**

<img src="https://github.com/MurtadaAhmed/YPH-YourPhotoHost/assets/108568451/a9c58c90-48cb-4649-bc28-04508b1d46ff" alt="Image view" width="500">

***************************

**All Uploaded Images view:**

<img src="https://github.com/MurtadaAhmed/YPH-YourPhotoHost/assets/108568451/2054a497-2f85-40c2-9b97-0a2d5dbd035f" alt="All Uploaded Images view" width="500"> 

***************************

**Reported Images view:**

<img src="https://github.com/MurtadaAhmed/YPH-YourPhotoHost/assets/108568451/9d85b14e-e2e8-46df-8793-3f4e060930f2" alt="All Uploaded Images view" width="500">

***************************

**Comment view:**

<img src="https://github.com/MurtadaAhmed/YPH-YourPhotoHost/assets/108568451/caa4e01a-7f6d-4c97-99bf-aae2ba4d32cd" width="500">  

***************************

**Profile view:**

<img src="https://github.com/MurtadaAhmed/YPH-YourPhotoHost/assets/108568451/9d15b51c-416f-466a-b9aa-c016d7b498ac" width="500">   

***************************
