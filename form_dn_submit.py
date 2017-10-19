#!/usr/bin/python

import re
import sys
import urllib
import urllib2
import webbrowser
from optparse import OptionParser

reload(sys)
sys.setdefaultencoding('utf8')

# dn inspection:
# https://www.democracynow.org/contact
# <form accept-charset="UTF-8" action="/contact/send_contact_email" method="post">

def main():

    requiredOpts="author,message".split(',')

    parser = OptionParser()
    parser.add_option("-u", "--url", dest="url",
        default='https://www.democracynow.org/contact/send_contact_email', help="url to submit FORM")
    parser.add_option("-a","--author", dest="author",
        default=False, help="author in \"Name <email>\" format")
    parser.add_option("-k", "--subkey", dest="subkey",
        default=52, help=("subject key "
                          "default: 52:Music submissions"))
    parser.add_option("-m", "--message", dest="message",
        default=False, help="message to submit FORM")
    parser.add_option("-s", "--subject", dest="subject",
        help="subject to submit FORM")
    (options, args) = parser.parse_args()

    #print options
    #import code; code.interact(local=dict(globals(), **locals()))

    for key,value in options.__dict__.items():
        if value is False:
            parser.error("parameter %s required" %key)

    names = process_author(options.author)
    if not names:
        parser.error("author %s format not found" %options.author)
    else:
        get_form(options,names)

def get_form(options,names):
    
    name = "%s %s" %names[0] names[1]
    data = urllib.urlencode({'contact[name]': name },
                            {'contact[email]': names[2] },
                            {'contact[to]': options.subkey },
                            {'contact[message]': options.message })
    full_url = options.url + '?' + data

    response = urllib2.urlopen(full_url)
    with open("results.html", "w") as f:
        f.write(response.read())
     
    webbrowser.open("form_dn_results.html") 
 
def process_author(author):

    # Define format
    r = re.compile('^.*\ .*\ <.*\>')

    # Split author/email
    if r.match(author) is None:
        return False 
    else:
        return author.split()

if __name__ == '__main__':
    main()
