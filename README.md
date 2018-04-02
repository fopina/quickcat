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

App is now up and running, though you still need to populate the DB with the categories you want and the image URLs to be categorized.

As heroku is not "file copying" friendly, let's connect to the mongo DB directly:
```
MONGODB_URI=$(heroku config:get MONGODB_URI) ./quickcat load_file PATH/TO/LIST_OF_IMAGE_URLS.txt
```

If your URL list is small you can just:
```
cat PATH/TO/LIST_OF_IMAGE_URLS.txt | heroku run ./quickcat load_file -
```

Then, don't forget to create the categories with
```
heroku run ./quickcat categories "CATEGORY 1" "CATEGORY 2" "...."
```

Now just share your herokuapp URL with the group!