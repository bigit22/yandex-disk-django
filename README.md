# Yandex Disk Integration with Django

This project demonstrates how to integrate Yandex.Disk API with a Django application. It allows users to authorize via OAuth, access public folders, and download files.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Environment Variables](#environment-variables)
- [License](#license)

## Features

- User authentication via Yandex OAuth.
- List files from a public Yandex.Disk folder.
- Download files from the Yandex.Disk.

## Requirements

- Python 3.x
- Django == 4.2.20
- Requests library
- python-dotenv

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/bigit22/yandex-disk-django.git
   cd yandex-disk-django

2. Create a virtual environment:

   ```python
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. Install the required packages:

   ```python
   pip install -r requirements.txt

4. Configure your Yandex OAuth credentials using environment variables. 
Create a .env file in the root of your project and add the following lines:

   ```text
   YA_CLIENT_ID=your_client_id
   YA_CLIENT_SECRET=your_client_secret

5. Migrate (for first launch)
   ```python
   python3 manage.py migrate

6. Start the server
   ```python
   python3 manage.py runserver

## Usage

1. Navigate to http://localhost:8000/ in your browser.
2. Click the link to authorize with Yandex.
3. After authorization, you will be redirected back to the app.
4. Enter the public key of the Yandex.Disk folder you wish to access.
5. View and download files from the specified folder.

## Environment Variables

Make sure to set the following environment variables to store your sensitive data securely:

    YA_CLIENT_ID: Your Yandex OAuth client ID.
    YA_CLIENT_SECRET: Your Yandex OAuth client secret.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
