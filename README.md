
# 📘 Projecte Escola — Gestió d’Alumnes, Professors i Classes

Aplicació web per gestionar les classes, alumnes i professors d'una escola, construïda amb **Python (Django)** i **MySQL**.  
Aquest projecte reutilitza una base de dades MySQL existent i ofereix una interfície d'administració completa sense haver de programar fitxers CRUD manuals.

---

## 🚀 Requisits previs

Assegura’t de tenir instal·lats:

- Python 3.10 o superior  
- MySQL Server i una base de dades existent  
- `pip` i `venv` per gestionar entorns virtuals  

---

## 🧱 Instal·lació

### 1. Crear i activar l’entorn virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Instal·lar dependències
Com que `mysqlclient` pot donar problemes de compilació, farem servir **PyMySQL**:

```bash
pip install django pymysql
```

---

## ⚙️ Configuració del projecte

### Configuració gitignore

Creem un fitxer `.gitingore` dels fitxes i carpetes que NO es pujaran al github:

```
# Entorn virtual
venv/
ENV/
env/

# Fitxers de compilació Python
__pycache__/
*.pyc
*.pyo
*.pyd

# Fitxers secrets o de configuració
.env
**/*.env

# Fitxers de base de dades locals
*.sqlite3

# Logs
*.log

# Fitxers del sistema operatiu
.DS_Store
Thumbs.db

# Fitxers temporals d'editor
.vscode/
.idea/

```


### 1. Crear el projecte i l’app principal

```bash
django-admin startproject appduoda
cd appduoda
python manage.py startapp gestio
```

Estructura resultant:
```
appduoda/
 ├── appduoda/
 │   ├── settings.py
 │   ├── urls.py
 │   └── ...
 ├── gestio/
 │   ├── models.py
 │   ├── admin.py
 │   └── ...
 └── manage.py
```

---

## 🗄️ Connexió amb MySQL

### Crear base de dades
```
CREATE DATABASE duoda CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE USER 'duoda_admin'@'localhost' IDENTIFIED BY 'ceduoda24';
GRANT ALL PRIVILEGES ON escola.* TO 'duoda_admin'@'localhost';

```

### Connectar amb la base de dades

Edita el fitxer `escola/settings.py` i afegeix la configuració de la teva base de dades:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'nom_de_la_teva_bd',
        'USER': 'usuari_mysql',
        'PASSWORD': 'contrasenya_mysql',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

import pymysql
pymysql.install_as_MySQLdb()
```

---

## 🧩 Generar models des de la base de dades existent

Django pot inspeccionar la base de dades i crear automàticament models Python basats en les teves taules actuals:

```bash
python manage.py inspectdb > gestio/models.py
```

> 📝 Després pots editar `models.py` per ajustar noms i relacions.

---

## 🧑‍🏫 Activar el panell d’administració

Edita `gestio/admin.py` i registra els models que vulguis administrar:

```python
from django.contrib import admin
from .models import *

admin.site.register(Alumnes)
admin.site.register(Professors)
admin.site.register(Classes)
```

> Canvia els noms segons els teus models generats.

---

## 🔐 Crear un superusuari

Per accedir al panell d’administració:

```bash
python manage.py createsuperuser
```

Introdueix usuari, correu i contrasenya.

---

## ▶️ Executar el servidor

Inicia el servidor local de desenvolupament:

```bash
python manage.py runserver
```

Obre el navegador a:

```
http://127.0.0.1:8000/admin/
```

Accedeix amb el teu usuari i ja podràs **veure, afegir i editar** alumnes, professors i classes des d’una interfície web completa.

---

## ⚙️ Migracions i nous camps

Quan afegeixis nous camps als models:

```bash
python manage.py makemigrations
python manage.py migrate
```

Les dades antigues tindran valor `NULL` als nous camps, a menys que indiquis un valor per defecte.

---

## 🧪 Comprovar la connexió amb la base de dades

Per obrir una shell SQL dins del teu entorn Django i provar la connexió:

```bash
python manage.py dbshell
```

També pots llistar models existents amb:

```bash
python manage.py showmigrations
```

Si no hi ha errors, la connexió amb MySQL funciona correctament.

---

## 💡 Properes millores

- Afegir vistes pròpies per a professors o alumnes.  
- Generar informes (PDF, Excel).  
- Afegir autenticació per rols (professor, administrador).  
- Millorar el disseny amb Django Templates o React.

---

## 🧾 Llicència

Projecte intern per a la gestió de classes. Pots adaptar-lo lliurement a les teves necessitats.
