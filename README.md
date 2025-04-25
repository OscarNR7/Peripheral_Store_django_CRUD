# 🛒 E-Commerce Admin Dashboard - Peripheral Store CRUD

A modular, scalable **Admin Dashboard** built with **Django** to manage the backend operations of an online computer peripherals store. This platform enables complete control over products, categories, users, orders, and more—supporting both administrative tasks and public catalog browsing.

---
## 📌 System Overview

This backend system is designed to streamline the management of a computer peripherals e-commerce store. It includes role-based access control, dynamic product specifications, order lifecycle management, and a responsive administrative interface—all optimized for usability, performance, and future integration.

---

## 👥 System Actors

| Actor                | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| **Administrator**    | Manages all areas: products, users, categories, orders, etc.                |
| **Public User**      | Can register, browse products, place orders, and manage addresses.          |
| **Django Admin**     | Uses Django’s built-in admin panel for low-level data operations.           |
| **PostgreSQL Database** | Backend database where all structured data is stored securely.           |
---

## ✅ Functional Requirements

| ID      | Name                      | Description                                                                                 |
|---------|---------------------------|---------------------------------------------------------------------------------------------|
| FR-01   | **User Registration**     | Register users with email, password, name, and auto-generated profile.                     |
| FR-02   | **User Authentication**   | Secure login with role-based access.                                                       |
| FR-03   | **Admin Dashboard**       | View statistics on orders, users, products, and revenue.                                   |
| FR-04   | **Profile Management**    | Users manage their profile info and multiple addresses.                                    |
| FR-05   | **Product Management**    | Full CRUD for products including images, specs, and inventory.                             |
| FR-06   | **Category Management**   | Create nested categories with custom attributes.                                            |
| FR-07   | **User Management**       | Admins manage user roles, activation status, and details.                                  |
| FR-08   | **Order Management**      | Update order and payment statuses across the order lifecycle.                              |
| FR-09   | **Product Catalog**       | Publicly accessible catalog with category filters and search.                              |
| FR-10   | **Address Management**    | Users manage multiple addresses with default shipping/billing.                             |
| FR-11   | **Order Item Management** | Admins can edit/remove individual items in orders and recalculate totals.                  |
| FR-12   | **Product Specifications**| Products include dynamic specifications based on category.                                 |

---

## 🚀 Non-Functional Requirements

| ID      | Name                       | Description                                                                                 |
|---------|----------------------------|---------------------------------------------------------------------------------------------|
| NFR-01  | **System Security**        | Role-based access ensures only authorized access to admin functions.                       |
| NFR-02  | **UI Responsiveness**      | Admin interfaces must respond within 5 seconds for CRUD actions.                           |
| NFR-03  | **Data Validation**        | All forms validate inputs both client- and server-side.                                    |
| NFR-04  | **Cross-Browser Compatibility** | System works on Chrome, Firefox, Safari, and Edge (latest versions).               |
| NFR-05  | **Error Recovery**         | System handles exceptions gracefully with clear messages.                                  |
| NFR-06  | **Pagination Performance** | Paginated lists (10–15 items) load in < 3 second.                                           |
| NFR-07  | **Image Optimization**     | Product images are optimized for web without quality loss.                                 |
| NFR-08  | **System Scalability**     | Database handles growth with efficient queries and indexing.                               |
| NFR-09  | **Form Usability**         | Multi-step forms provide user-friendly validation feedback.                                |
| NFR-10  | **Display Currency**       | All prices are shown in **Mexican Pesos (MXN)**.                                           |
| NFR-11  | **Dashboard Performance**  | Dashboard stats load within 3 seconds.                                                     |
| NFR-12  | **Search Responsiveness**  | Product searches respond in < 4 second for typical queries.                                |

---

## 🛠️ Technologies Used

- **Python 3**
- **Django**
- **PostgreSQL**
- **HTML/CSS/JS**
- *(Optionally: Tailwind CSS or Bootstrap for UI styling)*
