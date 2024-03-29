# ImageHub API

This API provides a comprehensive solution for image uploading and management, offering various features tailored to different user tiers, with additional flexibility for administrators.

## General info
* Users can upload images via HTTP request. Image should be in the format PNG or JPG. Maximum file size: 10 MB(Maximum size to be determined with the client.);
* Users can list their images;
  ![ImageHostingAPI/tests/media_for_tests/readme1.jpeg](ImageHostingAPI/tests/media_for_tests/readme1.png)
* There are three bultin account tiers: Basic, Premium and Enterprise;
* Users that have "Basic" plan after uploading an image get:
  - a link to a thumbnail that's 200px in height;
* Users that have "Premium" plan get:
  - a link to a thumbnail that's 200px in height;
  - a link to a thumbnail that's 400px in height;
  - a link to the originally uploaded image;
* Users that have "Enterprise" plan get;
  - a link to a thumbnail that's 200px in height;
  - a link to a thumbnail that's 400px in height;
  - a link to the originally uploaded image;
  - ability to fetch a link to the image that expires after a number of seconds (user can specify any number between 300 and 30000);
* Apart from the builtin tiers, admins can create arbitrary tiers with the following things configurable:
  - arbitrary thumbnail sizes;
  - presence of the link to the originally uploaded file;
  - ability to generate expiring links;
  - admin UI should be done via django-admin;

## How to set up the project

* Create docker containers for the project by running $ docker compose build;
* Start the application by launching the containers $ docker compose up;
* Superuser is created automatically, details for authorization below:
    * username='test'
    * password='test'