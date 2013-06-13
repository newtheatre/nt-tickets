# nt-tickets
nt-tickets is a self-contained Django project to provide a multi-occourence event ticket reservation front-end and back-end.

The project is being built for a redesign of the Nottingham New Theatre website, the aim is to provide a simple embedable show listing and ticket reservation system.

## Frontend
The current plan is to build frontends for:
- Displaying a list of shows, with date poster etc, all unstyled for including in a website.
- A 'current show' unstyled page for inclusion in website. Can show multiple categories of show
- An iframe-able ticket reservation form
- Cancelation page, via email link

![Ticket booking screenshot](http://github.com/fullaf/nt-tickets/raw/master/docs/screenshot_frontend.png)

## Backend
- Basic django admin for CRUD operations
- Reporting page for viewing ticket list

![Reporting screenshot](http://github.com/fullaf/nt-tickets/raw/master/docs/screenshot_backend.png)