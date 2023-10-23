import flask
import requests
import os
import shutil

# Flask App erstellen
app = flask.Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Datenbank erstellen
from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Datenbankschema festlegen
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    subdomains = db.Column(db.String(1000), nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'

with app.app_context():
    # Tabellen erstellen
    db.create_all()

# Cloudflare API URL, key und zone ID festlegen
CLOUDFLARE_API_URL = 'https://api.cloudflare.com/client/v4/zones/'
CLOUDFLARE_API_KEY = ''
CLOUDFLARE_ZONE_ID = '74ffdd22c7cc7eaf2bcc1c652285b680'

# Funktion zum Subdomain erstellen
def create_subdomain(subdomain, ip):
    # URL zusammenstellen
    url = CLOUDFLARE_API_URL + CLOUDFLARE_ZONE_ID + '/dns_records'
    # Daten für die Anfrage zusammenstellen
    data = {
        'type': 'A',
        'name': subdomain,
        'content': ip,
        'ttl': 120,
        'proxied': False
    }
    # Header für die Anfrage zusammenstellen
    headers = {
        'Authorization': 'Bearer ' + CLOUDFLARE_API_KEY,
        'Content-Type': 'application/json'
    }
    # API-Anfrage senden
    response = requests.post(url, json=data, headers=headers)
    # Statuscode überprüfen
    if response.status_code == 200:
        # Anfrage erfolgreich
        return True
    else:
        # Anfrage nicht erfolgreich
        return False

# Funktion zur Erstellung der NGINX-Konfiguration
def create_nginx_config(subdomain):
    # Dateinamen zusammenstellen
    filename = subdomain + '.conf'
    # Dateipfad zusammenstellen
    path = '/etc/nginx/sites-available/' + filename
    # Inhalt der Datei zusammenstellen
    content = f'''
server {{
    listen 80;
    server_name {subdomain}.bszgrm.de;

    root /var/www/subdomainman/{subdomain};
    index index.html index.htm;

    location / {{
        try_files $uri $uri/ =404;
    }}
}}
'''
    # Versuchen, die Datei zu erstellen und zu schreiben
    try:
        # Datei zum schreiben öffnen
        with open(path, 'w') as file:
            # Inhalt der Datei schreiben
            file.write(content)
        # symbolischen Link erstellen
        os.symlink(path, '/etc/nginx/sites-enabled/' + filename)
        return True
    except:
        return False

# Funktion zum erstellen vom Verzeichnis
def create_directory(subdomain):
    # Dateipfad zusammenstellen
    path = '/var/www/subdomainman/' + subdomain
    imgepath = path + '/images'
    try:
        # Verzeichnis erstellen
        os.mkdir(path)
        
        filename = 'index.html'
        # Dateipfad zusammenstellen
        path = '/var/www/subdomainman/' + subdomain + '/' + filename
        # Inhalt der Datei zusammenstellen
        content = f'''
    <!DOCTYPE html>
    <html>
        <head>
            <title>Subdomain erstellt!</title>
        </head>
        <body style="font-family: Arial;">
            <h1>Die Webseite wurde erfolgreich erstellt!</h1>
            <h2>Gehe nun zurück zum <a href="https://dash.bszgrm.de/dashboard">Subdomain-Manager</a> um eine neue <code>index.html</code> hochzuladen.</h2>
        </body>
    </html>
    '''
        # Versuchen, die Datei zu erstellen und zu schreiben
        try:
            # Datei zum schreiben öffnen
            with open(path, 'w') as file:
                # Inhalt der Datei schreiben
                file.write(content)
            return True
        except: 
            return False
    except:
        return False

def create_default_site(subdomain):
    # Dateinamen zusammenstellen
    filename = 'index.html'
    # Dateipfad zusammenstellen
    path = '/var/www/subdomainman/' + subdomain + '/' + filename
    # Inhalt der Datei zusammenstellen
    content = f'''
<!DOCTYPE html>
<html>
    <head>
        <title>Subdomain erstellt></title>
    </head>
    <body style="font-family: Arial;">
        <h1>Die Webseite wurde erfolgreich erstellt!</h1>
        <h2>Gehe nun zurück zum <a href="https://dash.bszgrm.de/dashboard">Subdomain-Manager</a> um eine neue <code>index.html</code> hochzuladen.</h2>
    </body>
</html>
'''
    # Versuchen, die Datei zu erstellen und zu schreiben
    try:
        # Datei zum schreiben öffnen
        with open(path, 'w') as file:
            # Inhalt der Datei schreiben
            file.write(content)
        return True
    except:
        return False

# Funktion zum Hochladen von Dateien
def upload_file(subdomain, file):
    # Dateipfad zusammenstellen
    path = '/var/www/subdomainman/' + subdomain + '/' + file.filename
    print("Dateipfad: ", path)
    try:
        # Datei speichern
        file.save(path)
        print("Datei erfolgreich gespeichert")
        return True
    except:
        print("Hochladen fehlgeschlagen")
        return False

def upload_image(subdomain, file):
    # Dateipfad zusammenstellen
    imagepath = '/var/www/subdomainman/' + subdomain + '/images'
    os.mkdir(imagepath)
    path = '/var/www/subdomainman/' + subdomain + '/images/' + file.filename
    print("Dateipfad: ", path)
    try:
        # Datei speichern
        file.save(path)
        print("Datei erfolgreich gespeichert")
        return True
    except:
        print("Hochladen fehlgeschlagen")
        return False

# Funktion zum Neuladen von Nginx
def reload_nginx():
    # Befehl festlegen
    command = 'sudo service nginx reload'
    try:
        # Befehl ausfuehren
        os.system(command)
        return True
    except:
        return False

# Funktion zur Loeschung von Subdomains
def delete_subdomain(subdomain):

    # Variablen festlegen
    email = "arthur.lehniger@gmail.com"
    api_key = CLOUDFLARE_API_KEY
    zone_id = CLOUDFLARE_ZONE_ID
    domain_name = subdomain + ".bszgrm.de"

    # Headers festlegen
    headers = {
        "Authorization": "Bearer ",
        "Content-Type": "application/json"
    }

    # Suchparameter festlegen
    params = {
        "type": "A",
        "name": domain_name
    }

    # GET-Anfrage an Cloudflare-API senden
    response = requests.get(f"https://api.cloudflare.com/client/v4/zones/74ffdd22c7cc7eaf2bcc1c652285b680/dns_records", headers=headers, params=params)
    print(response)

    # Ueberpruefen, ob die Anfrage erfolgreich war
    if response.status_code == 200:
        # Antwort als json speichern
        data = response.json()
        # Nach Uebereinstimmungen gucken
        if data["result"]:
            # Ergebnis holen
            record = data["result"][0]
            # ID herausfiltern
            print(f"The identifier of the DNS record for {domain_name} is {record['id']}")
            identifier = record['id']
        else:
            # Nichts gefunden
            print(f"No DNS record found for {domain_name}")
    else:
        # Anfrage nicht erfolgreich
        print(f"An error occurred: {response.status_code}")




    url = CLOUDFLARE_API_URL + CLOUDFLARE_ZONE_ID + '/dns_records?name=' + subdomain
    headers = {
        'Authorization': 'Bearer ' + CLOUDFLARE_API_KEY,
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        url = CLOUDFLARE_API_URL + CLOUDFLARE_ZONE_ID + '/dns_records/' + identifier

        response = requests.delete(url, headers=headers)

        if response.status_code == 200:

            print("Subdomain von Cloudflare geloescht")
            filename = subdomain + '.conf'
            path = '/etc/nginx/sites-available/' + filename
            try:
                os.remove(path)
                print("Nginx-Konfig geloescht")
                os.remove('/etc/nginx/sites-enabled/' + filename)
                print("Symbolischer Link geloescht")
                path = '/var/www/subdomainman/' + subdomain
                print("Pfad: ", path)
                try:
                    shutil.rmtree(path, ignore_errors=True)
                    # shutil.rmtree(sslpath, ignore_errors=True)
                    # print("SSL-Zertifikat geloescht")
                    print("Subdomainverzeichnis geloescht")
                    result = reload_nginx()
                    print("NGINX neu geladen")
                    if result:
                        print("Alles erfolgreich geloescht")
                        return True
                    else:
                        print("nginx konnte nicht neu geladen werden")
                        return False
                except:
                    print("Verzeichnis konnte nicht geloescht werden")
                    return False
            except:
                return False
                    

def delete_account1(username):
    user = User.query.filter_by(username=username).first()
    if user:
        subdomains = user.subdomains.split(',') if user.subdomains else []
        for subdomain in subdomains:
            result = delete_subdomain(subdomain)
            if result:
                continue
            else:
                return False
        db.session.delete(user)
        db.session.commit()
        return True
    else:
        return False
    
def create_ssl(subdomain):
    try:
        command = 'certbot --nginx -d ' + subdomain + '.bszgrm.de'
        os.system(command)
        return True
    except:
        return False

@app.route('/')
def index():
    return flask.render_template('index.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        password = flask.request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            return flask.render_template('register.html', error='Der Benutzername ist bereits vergeben.')
        else:
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            return flask.render_template('register.html', success='Sie haben sich erfolgreich registriert.')
    else:
        return flask.render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        password = flask.request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            flask.session['user'] = user.username
            return flask.redirect('/dashboard')
        else:
            return flask.render_template('login.html', error='Falscher Benutzername oder Passwort.')
    else:
        return flask.render_template('login.html')
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' in flask.session:
        username = flask.session['user']
        user = User.query.filter_by(username=username).first()
        subdomains = user.subdomains.split(',') if user.subdomains else []
        if flask.request.method == 'POST':
            subdomain = flask.request.form['subdomain'] + '.' + username
            if subdomain in subdomains:
                return flask.render_template('dashboard.html', username=username, subdomains=subdomains, error='Die Subdomain existiert bereits.')
            else:
                ip = '37.114.37.29'
                result = create_subdomain(subdomain, ip)
                if result:
                    result = create_nginx_config(subdomain)
                    if result:
                        result = create_directory(subdomain)
                        if result:
                            result = reload_nginx()
                            if result:
                                subdomains.append(subdomain)
                                user.subdomains = ','.join(subdomains)
                                db.session.commit()
                                return flask.render_template('dashboard.html', username=username, subdomains=subdomains, success='Die Subdomain wurde erfolgreich erstellt.')
                            else:
                                return flask.render_template('dashboard.html', username=username, subdomains=subdomains, error='Die nginx-Konfiguration konnte nicht neu geladen werden.')
                        else:
                            return flask.render_template('dashboard.html', username=username, subdomains=subdomains, error='Das Verzeichnis konnte nicht erstellt werden.')
                    else:
                        return flask.render_template('dashboard.html', username=username, subdomains=subdomains, error='Die nginx-Konfigurationsdatei konnte nicht erstellt werden.')
                else:
                    return flask.render_template('dashboard.html', username=username, subdomains=subdomains, error='Die Subdomain konnte nicht erstellt werden.')
        else:
            return flask.render_template('dashboard.html', username=username, subdomains=subdomains)
    else:
        return flask.redirect('/login')
@app.route('/upload', methods=['POST'])
def upload():
    if 'user' in flask.session:
        username = flask.session['user']
        user = User.query.filter_by(username=username).first()
        subdomains = user.subdomains.split(',') if user.subdomains else []
        subdomain = flask.request.form['subdomain']
        file = flask.request.files['file']
        if subdomain in subdomains:
            result = upload_file(subdomain, file)
            if result:
                return flask.render_template('dashboard.html', username=username, subdomains=subdomains, success='Die Datei wurde erfolgreich hochgeladen.')
            else:
                return flask.render_template('dashboard.html', username=username, subdomains=subdomains, error='Die Datei konnte nicht hochgeladen werden.')
        else:
            return flask.render_template('dashboard.html', username=username, subdomains=subdomains, error='Die Subdomain ist ungültig.')
    else:
        return flask.redirect('/login')
@app.route('/upload_image', methods=['POST'])
def upload_i():
    if 'user' in flask.session:
        username = flask.session['user']
        user = User.query.filter_by(username=username).first()
        subdomains = user.subdomains.split(',') if user.subdomains else []
        subdomain = flask.request.form['subdomain']
        file = flask.request.files['file']
        if subdomain in subdomains:
            result = upload_image(subdomain, file)
            if result:
                return flask.render_template('dashboard.html', username=username, subdomains=subdomains, success='Die Datei wurde erfolgreich hochgeladen.')
            else:
                return flask.render_template('dashboard.html', username=username, subdomains=subdomains, error='Die Datei konnte nicht hochgeladen werden.')
        else:
            return flask.render_template('dashboard.html', username=username, subdomains=subdomains, error='Die Subdomain ist ungültig.')
    else:
        return flask.redirect('/login')
@app.route('/delete/<subdomain>', methods=['POST'])
def delete(subdomain):
    if 'user' in flask.session:
        username = flask.session['user']
        user = User.query.filter_by(username=username).first()
        subdomains = user.subdomains.split(',') if user.subdomains else []
        if subdomain in subdomains:
            result = delete_subdomain(subdomain)
            if result:
                subdomains.remove(subdomain)
                user.subdomains = ','.join(subdomains)
                db.session.commit()
                return flask.render_template('dashboard.html', username=username, subdomains=subdomains, success='Die Subdomain wurde erfolgreich gelöscht.')
            else:
                return flask.render_template('dashboard.html', username=username, subdomains=subdomains, error='Die Subdomain konnte nicht gelöscht werden.')
        else:
            return flask.render_template('dashboard.html', username=username, subdomains=subdomains, error='Die Subdomain ist ungültig.')
    else:
        return flask.redirect('/login')
@app.route('/logout')
def logout():
    if 'user' in flask.session:
        flask.session.pop('user', None)
        return flask.render_template('index.html', success='Sie haben sich erfolgreich abgemeldet.')
    else:
        return flask.redirect('/')
@app.route('/delete_account', methods=['GET'])
def delete_account():
    if 'user' in flask.session:
        username = flask.session['user']
        result = delete_account1(username)
        if result:
            flask.session.pop('user', None)
            return flask.render_template('index.html', success='Ihr Account wurde erfolgreich gelöscht.')
        else:
            return flask.render_template('dashboard.html', error='Ihr Account konnte nicht gelöscht werden.')
    else:
        return flask.redirect('/login')
@app.route('/ssl/<subdomain>', methods=['POST'])
def ssl(subdomain):
    if 'user' in flask.session:
        username = flask.session['user']
        user = User.query.filter_by(username=username).first()
        result = create_ssl(subdomain)
        if result:
            return flask.render_template('dashboard.html', success='SSL-Zertifikat erfolgreich erstellt und angewendet.')
        else:
            return flask.render_template('dashboard.html', error='Beim Erstellen vom SSL-Zertifikat ist ein Fehler aufgetreten. Wahrscheinlich ist das rate-limit erreicht.')
@app.route('/browse/<subdomain>')
def browse(subdomain):
    FILE_SYSTEM_ROOT = '/var/www/subdomainman/' + subdomain
    itemList = os.listdir(FILE_SYSTEM_ROOT)
    return flask.render_template('browse.html', itemList=itemList)
@app.route('/browser/<subdomain>/<path:urlFilePath>')
def browser(urlFilePath, subdomain):
    FILE_SYSTEM_ROOT = '/var/www/subdomainman/' + subdomain
    nestedFilePath = os.path.join(FILE_SYSTEM_ROOT, urlFilePath)
    if os.path.isdir(nestedFilePath):
        itemList = os.listdir(nestedFilePath)
        fileProperties = {"filepath": nestedFilePath}
        if not urlFilePath.startswith("/"):
            urlFilePath = "/" + urlFilePath
        return flask.render_template('browse.html', urlFilePath=urlFilePath, itemList=itemList)
    if os.path.isfile(nestedFilePath):
        fileProperties = {"filepath": nestedFilePath}
        sbuf = os.fstat(os.open(nestedFilePath, os.O_RDONLY)) #Opening the file and getting metadata
        fileProperties['type'] = stat.S_IFMT(sbuf.st_mode) 
        fileProperties['mode'] = stat.S_IMODE(sbuf.st_mode) 
        fileProperties['mtime'] = sbuf.st_mtime 
        fileProperties['size'] = sbuf.st_size 
        if not urlFilePath.startswith("/"):
            urlFilePath = "/" + urlFilePath
        return flask.render_template('file.html', currentFile=nestedFilePath, fileProperties=fileProperties)
    return 'something bad happened'
# @app.route('/browse/<subdomain>/delete_file/')