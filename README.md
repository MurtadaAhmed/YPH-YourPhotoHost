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

To set up the YourPhotoHost application locally, follow these steps:

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

**Important:** make sure to change the database and the email server settings in settings.py


## Usage
1. Navigate to the application URL and sign up for a new account or log in if you already have one.

2. Once logged in, you can upload images by clicking on the "Upload New Image" button.

3. Manage your images in the "My Images" section, where you can view, edit, delete, and organize them into categories.

4. Explore other users' images and interact with them by liking, favoriting, and leaving comments.

## Features
- User authentication and account management
- Image upload and management (resize/rename/private or public/delete)
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

<img src="https://github.com/MurtadaAhmed/YPH-YourPhotoHost/assets/108568451/19e60106-fa6e-4361-b7b8-7da7ed44da61" alt="Guests homepage view" width="500"> 

***************************

**Authenticated users homepage view:**

<img src="https://github.com/MurtadaAhmed/YPH-YourPhotoHost/assets/108568451/a3029f9d-91a8-44ff-aa7b-54641cda151c" alt="Authenticated users homepage view" width="500"> 

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
