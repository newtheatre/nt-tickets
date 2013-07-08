# Tasks

## Show list
[x] posters
[x] description
[x] implement thumbnail generation
[x] set up calling of gen_thumbs() at a sensible point
[x] implement ordering of shows based on their start date, inhr from occurences
[x] hide link when show is passed or no tickets left
[x] show SOLD OUT if current and sold out
[x] show show category
[x] get settings passed to template to allow absolute URLs for booking link
[ ] clean up category and venue display

## Current show sidebar
[x] add categories to model
[x] define category order in settings or something (in db)
[x] build sidebar
[x] ignore cats with order=0
[x] make separate sidebar if there are no shows on in the next period
[ ] allow settting that period, and show it on the blank sidebar

## Show page
[ ] make individual show page

## Booking
[x] send email
[x] obey 'hours_til_close' parameter
[x] cancellation
[ ] refactor/cleanup

## Reporting
[x] print stylesheet
[x] link all pages together, main index?
[x] friendlier
[x] look into integrating with django admin (would be awesome)
[ ] clean up django admin implementation: rename in menu, remove add and change buttons
[ ] clean up django admin implementation: strip bootstrap-admin.css back to whats needed
	can be done on bootstrap website (90% can be removed)
