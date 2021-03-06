# grbcatalog.org

1. Overview

grbcatalog.org is an open source web application dedicated to
Gamma Ray Burst (GRB) studies. The data and the source code are
freely available in this repository for anyone to either contribute
or install at their own institution. The aim of the grbcatalog.org
project is to catalog all GRBs detected by various instruments and
build an online platform that GRB researches can quickly analyze
published data without having to painfully collect them from
published papers.

The grbcatalog.org features web based data analysis tools that
can be used by anyone with a web browser. These tools can create
publication quality plots for GRB researchers. System is written
in python based web application framework called django
(https://www.djangoproject.com/). In addition, it uses python
plotting library matplotlib (http://matplotlib.org/) to create
publication quality plots. The recommended database backend is
MySql (http://www.mysql.com/) but user may use any database
management system supported by django.

2.Description

The basic philosophy behind the design of grbcatalog.org web
application is to limit client side requirements to minimum.
Thereby allowing users with wide variety of devices to access
and use the web application. There can be multiple instances
of the web application so if one server is not working people
can use other available servers.
