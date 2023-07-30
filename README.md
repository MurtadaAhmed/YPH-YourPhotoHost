# YourPhotoHost (YPH)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-%3E%3D3.6-blue.svg)](https://www.python.org/downloads/)

## Overview
YourPhotoHost (YPH) is a web application that allows users to upload, view, and manage their images online. Users can create an account, upload images, and organize them into different categories. They can also like and favorite images, as well as leave comments on images uploaded by others.

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
- Like and favorite functionality
- Favorite or unfavorite functionality
- Commenting on images
- Moderators with special privileges for image moderation

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments
Special thanks to [Software University](https://softuni.bg/) team and their amazing teachers.

## Screenshots:
**Guests homepage view:**

![image](https://github.com/MurtadaAhmed/YPH-YourPhotoHost/assets/108568451/9dbb721a-2e6a-47a2-a3ae-52108b4afda7)

***************************

**Authenticated users homepage view:**

![image](https://github.com/MurtadaAhmed/YPH-YourPhotoHost/assets/108568451/be12269f-6963-41e8-ab16-926d67e9ffac)

***************************

**Image view:**

![image](https://github.com/MurtadaAhmed/YPH-YourPhotoHost/assets/108568451/c4fca0cf-7800-490e-bc94-37c556a285b6)

***************************

**All Uploaded Images view:**

![image](https://github.com/MurtadaAhmed/YPH-YourPhotoHost/assets/108568451/16948dd1-ef0b-484b-8b90-d801d8e7ec96)

***************************
