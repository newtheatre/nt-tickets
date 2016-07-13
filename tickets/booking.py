def book_landing(request, show_id):
    show = get_object_or_404(models.Show, id=show_id)
    if show.is_current() is False:
        return HttpResponseRedirect(reverse('error', kwargs={'show_id': show.id}))
    step = 1
    total = 2
    message = "Tickets for performances are reserved online and payed for on collection at the box office."
    foh_contact = 'foh@newtheatre.org.uk'

    if request.method == 'POST':    # If the form has been submitted...
        # A form bound to the POST data
        form = forms.BookingFormLanding(request.POST, show=show)
        if form.is_valid():     # All validation rules pass
            t = models.Ticket()
            person_name = form.cleaned_data['person_name']
            email_address = form.cleaned_data['email_address']

            t.person_name = person_name
            t.email_address = email_address
            # t.show = show
            occ_id = form.cleaned_data['occurrence']
            occurrence = models.Occurrence.objects.get(pk=occ_id)
            t.occurrence = occurrence
            if t.occurrence.date < datetime.date.today():
                return HttpResponseRedirect(reverse('error', kwargs={'show_id': show.id}))
            t.quantity = form.cleaned_data['quantity']
            if t.occurrence.maximum_sell < (t.occurrence.tickets_sold() + t.quantity):
                return HttpResponseRedirect(reverse('error', kwargs={'show_id': show.id}) + "?err=sold_out")

            try:
                tick = models.Ticket.objects.filter(
                    person_name=person_name,
                    email_address=email_address,
                    occurrence=occurrence
                )

                tick_ordered = tick.order_by('-stamp')[0]
                if tick_ordered.stamp > datetime.datetime.now() - datetime.timedelta(0, 5, 0):
                    return HttpResponseRedirect(reverse('error', kwargs={'show_id': show.id}) + "?err=time")
                else:
                    t.save()
            except IndexError:
                t.save()

            request.session["ticket"] = t

            email_html = get_template('email/confirm_inline.html').render(
                Context({
                    'show': show,
                    'ticket': t,
                    'settings': settings,
                    'customise': config,
                }))
            email_subject = 'Tickets reserved for ' + show.name
            email = EmailMessage(
                subject=email_subject,
                body=email_html,
                to=[t.email_address],
                from_email="boxoffice@newtheatre.org.uk"
            )
            email.content_subtype = 'html'

            if settings.ACTUALLY_SEND_MAIL == True:
                email.send()

            # Redirect after POST
            return HttpResponseRedirect(reverse('finish', kwargs={'show_id': show.id}))
    else:
        form = forms.BookingFormLanding(show=show)    # An unbound form

    return render(request, 'book_landing.html', {
        'form': form,
        'show': show,
        'step': step,
        'total': total,
        'message': message,
        'foh_contact': foh_contact,
    })

def book_finish(request, show_id):
    show = models.Show.objects.get(id=show_id)
    ticket = request.session["ticket"]

    return render(request, 'book_finish.html', {
        'show': show,
        'ticket': ticket,
    })

def book_error(request, show_id):
    if 'err' in request.GET:
        err = request.GET['err']
    else:
        err = None
    return render(request, 'book_error.html', {'err': err})

def cancel(request, ref_id):
    ticket = get_object_or_404(models.Ticket, unique_code=ref_id)
    if request.POST.get("id", "") == ticket.unique_code:
        ticket.cancelled = True
        ticket.save()
        cancelled = True
        already_cancelled = False
    elif ticket.cancelled is True:
        already_cancelled = True
        cancelled = False
    else:
        cancelled = False
        already_cancelled = False

    context = {
        'ticket': ticket,
        'cancelled': cancelled,
        'already_cancelled': already_cancelled,
    }

    return render(request, 'cancel.html', context)