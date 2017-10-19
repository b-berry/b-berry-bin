#!/usr/bin/python

#import mechanize
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

    requiredOpts="author,url".split(',')

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
        print 'success: %s' %names

    get_form(options,names)

def get_form(options,names):
    
    name = "%s %s" %names[0] names[1]
    data = urllib.urlencode({'contact[name]': name },
                            {'contact_email': names[3] },
                            {'contact[to]': options.subkey },
                            {'contact[message]': options.message })
    full_url = options.url + '?' + data

    response = urllib2.urlopen(full_url)
    with open("results.html", "w") as f:
        f.write(response.read())
     
    webbrowser.open("form_dn_results.html") 
 
#def get_form_mechanize(url):
#
#    # Set browser
#    br = mechanize.Browser()
#    br.set_handle_robots(False)
#    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
#
#    r = br.open(url)
#    html = r.read()
#    title = br.title()
#
#    # Sample from ipython
#    #In [24]: br.title()
#    #u'Contact Us | Democracy Now!'
#    #In [25]: for f in br.forms():
#    #    print f
#    #   ....:     
#    #<get https://www.democracynow.org/search application/x-www-form-urlencoded
#    #  <TextControl(query=)>>
#    #<post https://www.democracynow.org/contact/send_contact_email application/x-www-form-urlencoded
#    #  <HiddenControl(authenticity_token=i/IhBSNpD7ztyu9mlkBbv5xHfliQK2+bhqMjW/WYnP4=) (readonly)>
#    #  <TextControl(contact[name]=)>
#    #  <TextControl(contact[email]=)>
#    #  <SelectControl(contact[to]=[*, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65])>
#    #  <TextControl(contact[user_subject]=)>
#    #  <TextareaControl(contact[message]=)>
#    #  <TextControl(hobby=)>
#    #  <SubmitControl(commit=Send message) (readonly)>>
#    #<post https://www.democracynow.org/subscribe application/x-www-form-urlencoded
#    #  <HiddenControl(authenticity_token=i/IhBSNpD7ztyu9mlkBbv5xHfliQK2+bhqMjW/WYnP4=) (readonly)>
#    #  <TextControl(subscriber[email]=)>
#    #  <TextControl(hobby=)>
#    #  <SubmitControl(commit=subscribe) (readonly)>>

#    print title

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
