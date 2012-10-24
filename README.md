ResourceOverview
================

A tool that outputs a html file containing a table with the current AWS resources.

Uses Mako for the HTML templating and Boto for the AWS functions

	$ sudo easy_install Mako
	$ sudo easy_install boto 

The file gets the region and the credentials from the .boto file
	
~/.boto:
	
	[Boto]
	ec2_region_name = eu-west-1
	ec2_region_endpoint = eu-west-1.ec2.amazonaws.com
	
	[Credentials]
	aws_access_key_id = XXXXXXX
	aws_secret_access_key = YYYYYYYYYYYYYYY