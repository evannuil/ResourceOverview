#!/usr/bin/python
# aws_view_instances
#
# Author: E. van Nuil / Oblivion b.v.
# Project: Informa / Euroforum AWS
#
# Version 0.4
#
#   15-11-2012: 0.4 Adding Volume totals
#   12-09-2012: 0.3 Added Datatable (http://datatables.net)
#   11-09-2012: 0.2 Getting data and formatting
#   11-09-2012: 0.1 Initial setup, templating system
#
#   Uses Mako for the HTML templating and Boto for the AWS functions
#       sudo easy_install Mako
#       sudo easy_install boto 
#
#   The file gets the region and the credentials from the .boto file
#   ~/.boto:
#   [Boto]
#   ec2_region_name = eu-west-1
#   ec2_region_endpoint = eu-west-1.ec2.amazonaws.com
#
#   [Credentials]
#   aws_access_key_id = XXXXXXX
#   aws_secret_access_key = YYYYYYYYYYYYYYY
#

from mako.template import Template
from datetime import date
import datetime
import os
import boto
import boto.ec2

# TODO: Use proxy functions
ec2 = boto.connect_ec2()
reservations = ec2.get_all_instances()

# Get all instances
instance = reservations[0].instances[0]

# Get the HTML template
mytemplate = Template(filename='report/report.html')

# Get the date
now = datetime.datetime.now()

# Create the text buffer which is passed to the Mako render function
buf = ""

# Use the current date
today = date.today()

# Loop through all the reservations and instances
for r in reservations:
    for i in r.instances:
        buf += "<tr>"
        try:
            buf += "<td><b>%s</b> (%s)</td><td><span class='label label-" % (i.tags['Name'],i.id)
        except:
            buf += "<td><b>No Name!</b> (%s)</td><td><span class='label label-" % i.id
        if i.state == "running":
        	buf += "warning"
        else:
        	buf += "info"
        buf += "'>%s</span></td>\n" % i.state
        # Start Tags
        buf += "<td><div class=\"btn-group\">"
        buf += "<a class=\"btn btn-mini dropdown-toggle\" data-toggle=\"dropdown\" href=\"#\">"
        buf += "<i class=\"icon-tags\"></i> "
        buf += "<span class=\"caret\"></span></a>"
        buf += "<ul class=\"dropdown-menu\">"
        for key,value in i.tags.items():
            buf += "<li><a href=\"#\">%s: %s</a></li>" % (key,value)
        buf +=  "</ul></div></td>"
        # Start Addresses
        buf += "<td><div class=\"btn-group\">"
        buf += "<a class=\"btn btn-mini dropdown-toggle\" data-toggle=\"dropdown\" href=\"#\">"
        buf += "Info "
        buf += "<span class=\"caret\"></span></a>"
        buf += "<ul class=\"dropdown-menu\">"
        buf += "<li><a href=\"#\">Private ip: <b>%s</b></a></li>" % i.private_ip_address
        buf += "<li><a href=\"#\">Public ip: <b>%s</b></a></li>" % i.ip_address
        buf += "<li><a href=\"#\">Private DNS: <b>%s</b></a></li>" % i.private_dns_name
        buf += "<li><a href=\"#\">Public DNS: <b>%s</b></a></li>" % i.public_dns_name
        buf +=  "</ul></div></td>"
        # Start VPC
        buf += "<td>%s</td>" % i.vpc_id
        # Start Type
        try:
            if i.instance_type[0:2] == "m1":
                buf += "<td class=\"text-info\">%s</td>\n" % i.instance_type
            elif i.instance_type[0:2] == "c1":
                buf += "<td class=\"text-error\">%s</td>\n" % i.instance_type
            elif i.instance_type[0:2] == "t1":
                buf += "<td class=\"muted\">%s</td>\n" % i.instance_type
            else:
                buf += "<td class=\"text-warning\">%s</td>\n" % i.instance_type
        except:
            buf += "<td class=\"text-warning\">NaI</td>\n"
        buf += "<td>"
        if i.architecture == "i386":
            buf += "<span class=\"badge\">32"
        else:
            buf += "<span class=\"badge badge-info\">64"
        buf += "</span></td>"
        buf += "<td>"
        if i.monitored == True:
            buf += "<i class=\"icon-check\"></i>"
        buf += "</td>"
        # Start Volumes
        buf += "<td><div class=\"btn-group\">"
        buf += "<a class=\"btn btn-mini dropdown-toggle\" data-toggle=\"dropdown\" href=\"#\">"
        buf += "<i class=\"icon-hdd\"></i> "
        buf += "<span class=\"caret\"></span></a>"
        buf += "<ul class=\"dropdown-menu\">"
        totalvolumesize = 0
        for v in ec2.get_all_volumes(filters={'attachment.instance-id': i.id}):
            buf += "<li><a href=\"#" + v.id + "\">"
            buf += v.id + " (" + unicode(v.size) + "GB)"
            totalvolumesize += v.size
            buf += "</a></li>"
        buf +=  "</ul></div></td>"
        buf += "<td>" + unicode(totalvolumesize) + "</td>"
        buf += "</tr>\n"
buf += "</tbody>\n"
buf += "</table>"
totalvolumesizes = 0
for v in ec2.get_all_volumes():
    totalvolumesizes += v.size
buf += "<br/><hr>Total volume sizes: <b>" + unicode(totalvolumesizes) + " GB</b>"
# TODO: write to file with date in the file name to a S3 bucket.
output = mytemplate.render(date=today,data=buf)

# Write mode creates a new file or overwrites the existing content of the file.
# Write mode will _always_ destroy the existing contents of a file.
try:
    # This will create a new file or **overwrite an existing file**.
    f = open(("report/%s_report.html" % (today)), "w")
    try:
        f.writelines(output)  # Write a sequence of strings to a file
    finally:
        f.close()
except IOError:
    pass
