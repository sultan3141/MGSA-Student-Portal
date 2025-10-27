# MGSA Student Portal

**MGSA Student Portal** is a full-stack web application built with **Django** and **Django REST Framework**. It provides a comprehensive platform for school management, allowing students, executives, and administrators to interact with the system, access tutorials, resources, analytics, dashboards, and submit feedback.  

**Live Demo:** [https://zestful-optimism-mgsa-student-portal.up.railway.app/](https://zestful-optimism-mgsa-student-portal.up.railway.app/)

---

## Features

- **Admin Dashboard**
  - Geographical reports of students  
  - Export student data to CSV  
  - Student demographics and analytics  

- **Student Dashboard**
  - View and manage profile  
  - Access tutorials and resources  
  - Submit feedback  

- **Executive Dashboard**
  - School analytics and reports  
  - Student performance tracking  

- **Authentication**
  - User registration and login  
  - Role-based dashboard redirection  
  - Logout and forced logout  

- **RESTful API Endpoints**
  - `/api/auth/` → Authentication  
  - `/api/posts/` → Posts management  
  - `/api/resources/` → Resources  
  - `/api/tutorials/` → Tutorials  
  - `/api/analytics/` → Analytics  
  - `/api/executive/` → Executive operations  
  - `/api/student/` → Student-specific APIs  

- **Static & Media Handling**
  - Whitenoise for static files  
  - Cloudinary integration for media storage  

---

## Technologies Used

- **Backend:** Python 3.11, Django 5.2, Django REST Framework  
- **Frontend:** HTML, CSS, JavaScript  
- **Database:** PostgreSQL (Production on Railway)  
- **Deployment:** Railway.app  
- **Other Libraries:** Gunicorn, dj-database-url, django-cors-headers, django-filter, dj-rest-knox  

---

## Project Structure

