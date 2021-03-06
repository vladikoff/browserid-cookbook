#!/usr/bin/python

import cgi
import os
import requests

def print_header():
    print """<!DOCTYPE html><html><head><meta http-equiv="X-UA-Compatible" content="IE=Edge"></head>
<body>
<form id="login-form" method="POST">
<input id="assertion-field" type="hidden" name="assertion" value="">
</form>"""

def print_footer(email = 'null'):
    if email != 'null':
        email = '"%s"' % email

    print """
<script src="https://login.persona.org/include.js"></script>
<script>
navigator.id.watch({
    loggedInUser: %s,
    onlogin: function (assertion) {
        var assertion_field = document.getElementById("assertion-field");
        assertion_field.value = assertion;
        var login_form = document.getElementById("login-form");
        login_form.submit();
    },
    onlogout: function () {
        window.location = '?logout=1';
    },
});
</script>
</body></html>""" % email


def verify_assertion(assertion):
    audience = 'http://'
    if 'HTTPS' in os.environ:
        audience = 'https://'
    audience += os.environ['SERVER_NAME'] + ':' + os.environ['SERVER_PORT']

    try:
        page = requests.post('https://verifier.login.persona.org/verify',
                             verify=True,
                             data={ "assertion": assertion,
                                    "audience": audience})
        data = page.json
    except requests.exceptions.SSLError:
        data = { "status": "failed",
                 "reason": "Could not verify SSL certificate" }
    except requests.exceptions.ConnectionError:
        data = { "status": "failed",
                 "reason": "Could not connect to server" }

    return data

print 'Content-type: text/html\n\n'

form = cgi.FieldStorage()
if 'assertion' in form:
    result = verify_assertion(form['assertion'].value)
    if result['status'] == 'okay':
        print_header()
        print "<p>Logged in as: " + result['email'] + "</p>"
        print "<p><a href=\"javascript:navigator.id.logout()\">Logout</a></p>"
        print '<p><a href="python.cgi">Back to login page</a></p>'
        print_footer(result['email'])
    else:
        print_header()
        print "<p>Error: " + result['reason'] + "</p>"
        print '<p><a href="python.cgi">Back to login page</a></p>'
        print_footer()
elif 'logout' in form:
    print_header()
    print '<p>Logged out.</p>'
    print '<p><a href="python.cgi">Back to login page</a></p>'
    print_footer()
else:
    print_header()
    print "<p><a href=\"javascript:navigator.id.request()\">Login</a></p>"
    print_footer()
