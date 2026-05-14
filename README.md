# AetherMap – Drone Flight Registration & Agricultural Service Platform

AetherMap is a comprehensive web-based platform developed as an MCA mini project to streamline drone flight approvals and agricultural drone service management.  
The platform integrates drone regulation, flight request management, and farmer-service provider connectivity into a single ecosystem.

---

## Project Overview

AetherMap is designed to ensure safe, legal, and efficient drone operations by providing:

- Drone flight approval management
- Drone zone classification
- Agricultural drone service marketplace
- Flight certificate generation
- Farmer and service provider collaboration

The platform enables drone users to register flight plans for approval while allowing farmers to request drone-based agricultural services such as crop spraying and aerial surveying.

---

## Key Features

-  Interactive Drone Zone Management
-  Drone Flight Registration System
-  Flight Approval Workflow
-  PDF Certificate Generation
-  Farmer Service Request Module
-  Drone Service Provider Marketplace
-  Role-Based Authentication System
-  User Dashboard & Notifications
-  Responsive User Interface
-  Secure Backend Architecture

---

## User Roles

### Drone Users
- Register drones
- Submit flight plans
- View approval status
- Download flight certificates

### Farmers
- Request agricultural drone services
- View available service providers
- Track request approvals

### Service Providers
- Register drone services
- Manage service availability
- Accept farmer requests

### Admin
- Approve/reject flight requests
- Manage drone zones
- Monitor users and services

---

## Technology Stack

### 🔹 Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript (ES6+)

### 🔹 Backend
- Python
- Django Framework

### 🔹 Database
- PostgreSQL

### 🔹 Additional Tools
- Git & GitHub
- VS Code
- FPDF / ReportLab (PDF Generation)

---

## Core Modules

### Drone Zone Management
Displays permitted and restricted drone flying zones.

### Flight Request Management
Allows drone users to submit detailed flight plans.

### Certificate Generation
Generates approval certificates for authorized flights.

### Farmer Service Request Module
Allows farmers to request drone-based agricultural services.

### Service Provider Module
Enables providers to register and manage services.

### Notification System
Sends approval and request status updates.

---

## Project Structure

```bash
AetherMap/
│
├── static/                   # CSS, JS, Images
├── templates/                # HTML Templates
├── media/                    # Uploaded Files
├── screenshots/              # Project Screenshots
├── drone_app/                # Main Django App
├── manage.py
├── requirements.txt
├── README.md
└── .gitignore
```
---
## Installation & Setup

### Clone Repository

git clone https://github.com/jeesonjustin/AetherMap-Drone-Registration.git

### Navigate to Project Folder

cd AetherMap-Drone-Registration

### Create Virtual Environment

python -m venv venv

### Activate Virtual Environment

venv\Scripts\activate

### Install Dependencies

pip install -r requirements.txt

### Run Migrations

python manage.py migrate

### Start Development Server

python manage.py runserver

### Open in Browser

http://127.0.0.1:8000/

## User Interface

#### Home Page

![Landing page of AetherMap showing drone zone tracking, flight registration options, navigation menu, and service access sections for drone users and farmers.](<screenshots/Landing page.png>)

#### Login Page

![AetherMap login interface with username and password fields for secure user authentication.](screenshots/Login.png)

#### My Drone Registration Page

![Drone user dashboard displaying approved drone registrations, registration details, and certificate download options.](<screenshots/My drone registration .png>)

#### My Drone Registration Pending Page

![Drone registration status page showing pending approval requests submitted by the drone user.](<screenshots/My drone registration pending.png>)

#### Drone Registration Form Page

![Drone registration form allowing users to enter personal details, drone specifications, and flight information for approval.](<screenshots/NewDrone reg_form.png>)

#### Red Zone Alert

![Warning interface indicating restricted drone flying zone with red zone alert notification and flight restriction message.](<screenshots/Red zone alert .png>)

#### Role Based Access Cards

![Role selection cards for Drone User, Farmer, and Service Provider access within the AetherMap platform.](<screenshots/Role based access cards.png>)

#### Admin Dashboard Page

![Admin dashboard displaying drone registration requests, user management options, and platform monitoring controls.](<screenshots/Admin dashboard1.png>)

#### Drone Registration Management Page

![Administrative drone registration management page showing approval, rejection, and monitoring options for submitted drone requests.](<screenshots/Drone reg management2.png>)

---
## Workflow

Users register as:
- Drone User
- Farmer
- Service Provider

Drone users submit flight requests.

Admin verifies and approves requests.

Approved users receive digital certificates.

Farmers can request drone-based agricultural services.

Service providers connect with farmers and fulfill requests.

---
## Objectives

- Simplify drone flight approval workflow
- Ensure legal and safe drone operations
- Connect farmers with drone service providers
- Create a centralized drone management system

---

## Future Enhancements

- Real-time Drone Tracking Map
- Live Weather Alerts
- Mobile Application
- Interactive Drone Zone Mapping
- Automated PDF Certificate Validation

---

## Academic Information

Project Title: AetherMap- Drone Flight Registration & Agricultural Service Platform

Course: Master of Computer Applications (MCA)

Institution: SCMS School of Engineering and Technology

University: APJ Abdul Kalam Technological University

---

## Developed By

Jeeson Justin
MCA Student | UI/UX Designer | Full Stack Developer

- GitHub: https://github.com/jeesonjustin
- LinkedIn: https://linkedin.com/in/jeesonjustin

---


