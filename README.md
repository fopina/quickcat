# QuickCat
Quickly Categorize images

## DISCLAIMER

This a pre-alpha-alpha version of whatever this application could be.

There is no authentication at all nor bot / duplicated votes protection.  
As there is no auth, there isn't any other kind of protection either (CSRF, etc).  

It is meant to be used by closed groups (with trustworthy people) to quickly go through a set of images and then use them with Tensorflow (or whatever).  

Results will be as reliable as your workgroup!


## QUICKSTART

This repo is heroku friendly.  

Starting your own instance (using GIT and heroku CLI) is as easy as:

```
git clone http://github.com/fopina/quickcat/
cd quickcat
heroku apps:create
heroku addons:create mongolab
git push heroku master
```