# nt-tickets
[![Build Status](https://travis-ci.org/newtheatre/nt-tickets.svg?branch=master)](https://travis-ci.org/newtheatre/nt-tickets)
[![Coverage Status](https://coveralls.io/repos/newtheatre/nt-tickets/badge.svg?branch=master&service=github)](https://coveralls.io/github/newtheatre/nt-tickets?branch=master)

nt-tickets is a self-contained Django project to provide a multi-occurrence event ticket reservation frontend and backend.

The project was built for a redesign of the Nottingham New Theatre website (http://newtheatre.org.uk), the aim was to provide a simple embeddable show listing and ticket reservation system.

The next stage of the project is to refactor some of the code to make it easier to deploy/customise for other venues.

## Frontend
The project at the current stage can:
- Display a list of shows, with date poster etc, all unstyled for including in a website. This is currently achieved using raw HTML, a JSON API is in the works.
- A 'current show' raw page for inclusion in website. Can show multiple categories of show, such as in-house and external shows.
- An iframe-able ticket reservation form.
- Cancellation page, via email link.

![Ticket booking screenshot](http://github.com/fullaf/nt-tickets/raw/master/docs/screenshot_frontend.png)

## Backend
Uses django admin for CRUD for shows, occurrences, categories and viewing reservations. Reservation viewing is achieved with a custom admin page for the ticket model.
