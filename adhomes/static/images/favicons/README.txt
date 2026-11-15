A.D Homeshelter LTD — website favicon files

For a Django project, copy these files to:
  <your_static_directory>/images/favicon/

In the <head> of your base template, make sure {% load static %} is available,
then add:

<link rel="icon" href="{% static 'images/favicon/favicon.ico' %}" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="{% static 'images/favicon/favicon-32x32.png' %}">
<link rel="icon" type="image/png" sizes="16x16" href="{% static 'images/favicon/favicon-16x16.png' %}">
<link rel="apple-touch-icon" sizes="180x180" href="{% static 'images/favicon/apple-touch-icon.png' %}">
<link rel="manifest" href="{% static 'images/favicon/site.webmanifest' %}">

Note: The manifest assumes your production static URL is /static/.
Adapt paths if your Django STATIC_URL differs. Run collectstatic when deploying.
