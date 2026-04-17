[![Review Assignment Due Date](httpsclassroom.github.comassetsdeadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](httpsclassroom.github.comaF1hjDb63)

# Environment Setup

This project uses Python 3.12 and a local virtual environment
for dependency management.

## Prerequisites

Before starting, make sure you have

-   Python 3.12.x installed
-   Git installed
-   A terminal such as PowerShell or Command Prompt

Verify Python

``` powershell
py -3.12 --version
```

## Environment Variables

Before running the server, create a `.env` file in the project root and
add your Google OAuth and Amazon S3 credentials:

``` env
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
AWS_ACCESS_KEY_ID=
AWS_S3_REGION_NAME=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
DATABASE_URL=
```

------------------------------------------------------------------------

# CS3240 Project -- Quick Start

## Clone the Repository

``` powershell
git clone https://github.com/uva-cs3240-s26/project-a-13.git
```

Clones the project repository from GitHub to your local machine.

## Enter the Project Folder

``` powershell
cd project-a-13
```

Moves into the project directory so all following commands run in the
correct location.

## Create a Virtual Environment

``` powershell
py -3.12 -m venv .venv
```

Creates a Python 3.12 virtual environment named `.venv` to isolate
project dependencies.

## Activate the Virtual Environment

``` powershell
.\.venv\Scripts\Activate.ps1
```

Activates the virtual environment so Python and pip use the project's
environment.

## Install Dependencies

``` powershell
pip install -r requirements.txt
```

Installs all required Python packages listed in `requirements.txt`.

## Apply Database Migrations

``` powershell
python manage.py migrate
```

Applies database migrations to create the necessary database tables for
the Django application.

## Run the Development Server

``` powershell
python manage.py runserver
```

Starts the Django development server so you can access the application
locally in your browser.

------------------------------------------------------------------------

