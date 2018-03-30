![release-version-badge](https://img.shields.io/github/tag/Epse/EpPos.svg) ![travis-CI-badge](https://img.shields.io/travis/Epse/EpPos.svg)
# EpPos
EpPos is a basic Django (python)-based Point Of Sale
system that is designed to be platform-independent (it runs on the web) and completely mobile- and
touch-friendly. 

**Contributors: see the [CONTRIBUTING](CONTRIBUTING.md) file!**

## What is a POS?
A POS (Point Of Service) system is the software that is used by cashiers and waiters to bill you and keep the stock.
This one is meant for smaller businesses, like food trucks.

## How can I run it?
It is very simple. Have a look at the wiki! Or read this block of text since the wiki isn't yet up-to-date.

First off, install Python 3 and Django. If you are using Linux, they are probably in your repo's.
Then [download EpPos](https://github.com/Epse/EpPos/releases) to wherever you want to keep your Django apps, edit settings.py
and change the `DEBUG` var to `False` and add the domain name or IP-address from which the POS will
be accessed to the `ALLOWED_HOSTS` variable. Then run `python manage.py migrate` and `python
manage.py createsuperuser` to create a new admin account which you can use to manage the system and
add new users.
Then set it up like you would set up any normal Django application, we recommend using
[uWSGI](http://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html) with nginx.

If you need help with this, you can send me an email.

## Known "issues"
- There is a limitation in the total value of an order. It cannot exceed 10 digits, counting decimal places. If someone runs into this: congratulations, I'll have to update this.

## I found a bug
Congratulations! You can report this issue on the issue tracker on GitHub. I will be
forever grateful if you could possible be so kind as to include a server log and/or web console log.

## I want to help!
Absolutely marvelous! Have a look in the [CONTRIBUTING](CONTRIBUTING.md) file for info about contributing!

## I want to make a spinoff!
You absolutely may. If you think what you want in a POS is not something that is in the scope of
EpPOS (although you may always ask) you can for sure just fork it. Details are in the LICENSE file,
we use the Apache license.

## Maintainers aka. Who Do I Talk To?
Epse aka. Stef Pletinck

## Hall of fame
Everyone who contributes to EpPos gets a spot here.
* [Sebastien Spaeth](https://github.com/spaetz)
* @manuelfedele
