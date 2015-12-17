import mailchimp
import settings

def get_mailchimp_api():
    if settings.MAILCHIMP_APIKEY:
        return mailchimp.Mailchimp(settings.MAILCHIMP_APIKEY)
    else:
        return None

def subscribe(email, first_name, last_name):
    try:
        m = get_mailchimp_api()
        m.lists.subscribe(settings.MAILCHIMP_LIST, {
            'email':email,
            'email_type':'html',
            'merge_vargs': {
                'FNAME': first_name,
                'LANME': last_name,
            },
        })
        return True
    except mailchimp.ListAlreadySubscribedError:
        print 'already subscribed '+email
        return False
    except mailchimp.Error, e:
        print e
        return False
