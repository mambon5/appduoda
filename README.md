# 📘 Projecte Escola — Gestió d’Alumnes, Professors i Classes

Aplicació web per gestionar les classes, alumnes i professors d'una escola, construïda amb **Python (Django)** i **MySQL**.

Aquesta aplicació permet portar un control exhaustiu dels pagaments dels alumnes, el registre de les classes realitzades i els pagaments als professors.

---

## 🏗️ Estructura del Projecte

L'aplicació segueix l'arquitectura estàndard de Django:

```text
appduoda/
├── appduoda/           # Configuració global del projecte
│   ├── settings.py     # Configuració (DB, Apps, Middleware)
│   └── urls.py         # Rutes principals
├── gestio/              # Aplicació de gestió (Lògica de negoci)
│   ├── models.py       # Definició de dades (Alumne, Professor, Classe, Pagaments)
│   ├── admin.py        # Configuració del Panell d'Administració
│   └── migrations/     # Historial de canvis a la Base de Dades
├── venv/               # Entorn virtual de Python
├── manage.py           # Gestor de comandes de Django
└── .env                # Fitxer de configuració de variables d'entorn
```

---

## 🚀 Com executar en un servidor

### 1. Preparació de l'entorn
Si encara no ho has fet, clona el repositori i crea l'entorn virtual:
```bash
python3 -m venv venv
source venv/bin/activate
pip install django pymysql cryptography
```

### 2. Configuració de la Base de Dades
Assegura't de tenir un fitxer `.env` a l'arrel amb les credencials:
```env
DB_NAME=appceduoda
DB_USER=duoda_admin
DB_PASSWORD=xxxx
DB_HOST=localhost
```

### 3. Aplicar canvis i crear usuari
Executa les migracions per crear les taules a MySQL i crea el teu usuari d'accés:
```bash
python3 manage.py migrate
python3 manage.py createsuperuser
```

### 4. Execució en desenvolupament
Per treballar localment:
```bash
python3 manage.py runserver
```
Això obrirà l'app a `http://127.0.0.1:8000/`.

### 5. Execució en un servidor (producció bàsica)
Si vols que l'app sigui accessible des d'altres ordinadors:
```bash
python3 manage.py runserver 0.0.0.0:8000
```
*Nota: Per a producció real es recomana utilitzar Gunicorn + Nginx.*

---

## 🛠️ Com funciona l'aplicació

L'aplicació es gestiona íntegrament des del **Panell d'Administració**:

1. **Alumnes i Professors**: Primer registra els teus professors (amb el seu preu/hora) i els teus alumnes.
2. **Classes**: Cada vegada que es realitzi una classe, registra-la al sistema indicant la data, l'alumne, el professor i el preu que ha de pagar l'alumne.
3. **Pagaments d'Alumnes**: Registra quan un alumne fa un pagament a l'escola (Efectiu, Bizum o Transferència).
4. **Pagaments a Professors**: Registra quan l'escola liquida les classes a un professor.

### Avantatges:
- **Panell de Professors**: Els professors poden registrar les seves pròpies classes un cop loguejats.
- **Pagament de Pares**: Pàgina de pagament ràpida amb càlcul automàtic de preu segons l'alumne.
- **Filtres**: Pots filtrar ràpidament quines classes ha fet un professor o quins pagaments ha fet un alumne.
- **Historial**: Tens un registre històric totalment traçable de tota l'activitat econòmica de l'escola.

---

## ⚙️ Manteniment

Si afegeixes nous camps als models:
1. Edita `gestio/models.py`.
2. Executa `python manage.py makemigrations`.
3. Executa `python manage.py migrate`.

---

## 🧾 Llicència
Projecte intern de gestió per a CE Duoda.
