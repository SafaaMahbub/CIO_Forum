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

------------------------------------------------------------------------

## Quick Start

``` powershell
git clone httpsgithub.comuva-cs3240-s26project-a-13.git
cd project-a-13
py -3.12 -m venv .venv
..venvScriptsActivate.ps1
pip install -r requirements.txt
python manage.py runserver
```

------------------------------------------------------------------------

## Verify installation

``` powershell
python -m django --version
```

Expected

    4.2.27

You can also verify the virtual environment



Both paths should point to `.venvScripts`.

------------------------------------------------------------------------

## 6. Run the Django development server

``` powershell
python manage.py runserver