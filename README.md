#Buscando
Buscando is a Django app that matches volunteers and families of undocumented minors to organizations who have resources to help.

### Development

1. Clone this repo.

2. Install django and other dependecies.

        pip install -r requirements.txt

3. Start up the server.
    
        python manage.py runserver

4. View the project at `http://localhost:8000/app`

### Editing CSS

1. Install Ruby (if needed) and Compass:

        http://compass-style.org/install/

2. Make changes to /app/static/*.scss files

3. Watch for changes to *.scss files

        compass watch app/static

Note: Don't modify /app/static/*.css
