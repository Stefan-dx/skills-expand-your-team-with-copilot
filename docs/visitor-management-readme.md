# Besucherverwaltungssystem / Visitor Management System

Ein webbasiertes System zur Verwaltung von Besuchern mit NFC- und QR-Code-Pässen.

A web-based system for managing visitors with NFC and QR code passes.

---

## 📋 Übersicht / Overview

### Deutsch

Das Besucherverwaltungssystem ermöglicht die Registrierung und Verwaltung von Besuchern mit verschiedenen Pass-Typen:
- **Blanko-Pässe**: Temporäre Pässe für einmalige oder kurzfristige Besuche
- **Langzeitpässe**: Dauerhafte Pässe für regelmäßige Besucher

Besucher können sich mit einem Blanko-Pass registrieren oder erhalten einen Langzeitpass. Das System unterstützt Check-in und Check-out über NFC-Chips oder QR-Codes.

**Wichtige Funktionen:**
- Besucherregistrierung mit Pass-Zuweisung
- Check-in/Check-out über NFC oder QR-Code
- Echtzeit-Anwesenheitsverfolgung
- Cloud-Synchronisation für Feuerwehr-Compliance (Gebäuderäumung)
- Besucherverlauf und Berichte

### English

The Visitor Management System allows registration and management of visitors with different pass types:
- **Blank Passes**: Temporary passes for one-time or short-term visits
- **Long-term Passes**: Permanent passes for regular visitors

Visitors can register with a blank pass or receive a long-term pass. The system supports check-in and check-out via NFC chips or QR codes.

**Key Features:**
- Visitor registration with pass assignment
- Check-in/check-out via NFC or QR code
- Real-time presence tracking
- Cloud synchronization for fire department compliance (building evacuation)
- Visitor history and reports

---

## 🏗️ Architektur / Architecture

### Technologie-Stack / Technology Stack

- **Backend**: Python FastAPI
- **Datenbank / Database**: MongoDB
- **Frontend**: HTML, CSS, JavaScript
- **API-Dokumentation / API Documentation**: OpenAPI (Swagger)

### Projektstruktur / Project Structure

```
src/
├── app.py                          # Hauptanwendung / Main application
├── backend/
│   ├── models/                     # Datenmodelle / Data models
│   │   ├── visitor.py              # Besuchermodell
│   │   ├── pass_model.py           # Passmodell
│   │   └── checkinout.py           # Check-in/out-Modell
│   ├── services/                   # Geschäftslogik / Business logic
│   │   ├── visitor_service.py      # Besucherverwaltung
│   │   ├── pass_service.py         # Pass-Verwaltung
│   │   ├── checkinout_service.py   # Check-in/out-Logik
│   │   └── cloud_sync_service.py   # Cloud-Synchronisation
│   ├── routers/                    # API-Endpunkte / API endpoints
│   │   ├── visitors.py             # Besucher-Endpunkte
│   │   ├── passes.py               # Pass-Endpunkte
│   │   └── checkinout.py           # Check-in/out-Endpunkte
│   └── database.py                 # Datenbankkonfiguration
└── static/                         # Frontend-Dateien
```

---

## 🚀 Installation und Setup / Installation and Setup

### Voraussetzungen / Prerequisites

- Python 3.8 oder höher / Python 3.8 or higher
- MongoDB (läuft auf localhost:27017)
- pip (Python-Paketmanager)

### Installation

1. **Repository klonen / Clone repository:**
   ```bash
   git clone <repository-url>
   cd skills-expand-your-team-with-copilot
   ```

2. **Abhängigkeiten installieren / Install dependencies:**
   ```bash
   pip install -r src/requirements.txt
   ```

3. **MongoDB starten / Start MongoDB:**
   ```bash
   # Stellen Sie sicher, dass MongoDB läuft
   # Make sure MongoDB is running
   mongod
   ```

4. **Anwendung starten / Start application:**
   ```bash
   cd src
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Anwendung öffnen / Open application:**
   - Weboberfläche / Web interface: http://localhost:8000
   - API-Dokumentation / API docs: http://localhost:8000/docs

---

## 📚 API-Dokumentation / API Documentation

### Besucher-Endpunkte / Visitor Endpoints

#### Besucher registrieren / Register Visitor
```http
POST /visitors/register
Content-Type: application/json

{
  "first_name": "Max",
  "last_name": "Mustermann",
  "email": "max.mustermann@example.com",
  "phone": "+49 123 456789",
  "company": "Example GmbH",
  "pass_id": "BLANK-001",
  "pass_type": "blank"
}
```

#### Alle Besucher abrufen / Get All Visitors
```http
GET /visitors?active_only=false
```

#### Besucher nach Pass-ID suchen / Get Visitor by Pass ID
```http
GET /visitors/pass/{pass_id}
```

### Pass-Endpunkte / Pass Endpoints

#### Verfügbare Pässe abrufen / Get Available Passes
```http
GET /passes/available?pass_type=blank
```

#### Pass validieren / Validate Pass
```http
POST /passes/{pass_id}/validate
```

### Check-in/out-Endpunkte / Check-in/out Endpoints

#### Check-in durchführen / Perform Check-in
```http
POST /checkinout/checkin
Content-Type: application/json

{
  "pass_id": "BLANK-001",
  "method": "nfc",
  "location": "Haupteingang"
}
```

#### Check-out durchführen / Perform Check-out
```http
POST /checkinout/checkout
Content-Type: application/json

{
  "pass_id": "BLANK-001",
  "method": "qr",
  "location": "Haupteingang"
}
```

#### Anwesende Besucher abrufen / Get Present Visitors
```http
GET /checkinout/present
```

#### Anwesenheitsbericht generieren / Generate Presence Report
```http
GET /checkinout/report/presence
```

Weitere Details finden Sie in der interaktiven API-Dokumentation unter: http://localhost:8000/docs

For more details, see the interactive API documentation at: http://localhost:8000/docs

---

## 🔥 Feuerwehr-Compliance / Fire Department Compliance

Das System aktualisiert automatisch eine Cloud-Datei bei jeder Anwesenheitsänderung. Diese Datei enthält:

The system automatically updates a cloud file on every presence change. This file contains:

- Gesamtzahl anwesender Besucher / Total number of present visitors
- Detaillierte Liste aller anwesenden Personen / Detailed list of all present persons
- Check-in-Zeitstempel / Check-in timestamps
- Letzte Aktualisierungszeit / Last update time

**Zugriff auf die Datei / Access the file:**
```http
GET /checkinout/sync/data
```

Die Datei wird auch lokal gespeichert unter / The file is also stored locally at:
```
./visitor_presence.json
```

---

## 🔐 Sicherheit / Security

### Best Practices

1. **Pass-Validierung / Pass Validation**: Alle Pässe werden vor der Verwendung validiert
2. **Eindeutige IDs / Unique IDs**: Jeder Besucher und Pass hat eine eindeutige ID
3. **Zeitstempel / Timestamps**: Alle Aktionen werden mit Zeitstempeln versehen
4. **Cloud-Sync / Cloud Sync**: Automatische Synchronisation bei Statusänderungen

### Produktionsumgebung / Production Environment

Für die Produktion sollten Sie:
- HTTPS verwenden / Use HTTPS
- Authentifizierung hinzufügen / Add authentication
- Cloud-Storage integrieren (AWS S3, Azure Blob, etc.)
- Backup-Strategien implementieren / Implement backup strategies

---

## 🧪 Tests / Testing

Die API kann über die interaktive Swagger-Oberfläche getestet werden:
The API can be tested through the interactive Swagger interface:

http://localhost:8000/docs

### Beispiel-Workflow / Example Workflow

1. **Pass erstellen / Create Pass** (bereits initialisiert / already initialized)
2. **Besucher registrieren / Register Visitor**
3. **Check-in durchführen / Perform Check-in**
4. **Anwesenheit prüfen / Check Presence**
5. **Check-out durchführen / Perform Check-out**

---

## 📊 Datenmodelle / Data Models

### Besucher / Visitor
- `visitor_id`: Eindeutige ID
- `first_name`: Vorname
- `last_name`: Nachname
- `email`: E-Mail-Adresse
- `phone`: Telefonnummer (optional)
- `company`: Firma (optional)
- `pass_id`: Zugewiesene Pass-ID
- `pass_type`: Pass-Typ ('blank' oder 'longterm')
- `is_active`: Aktuell anwesend
- `created_at`: Erstellungsdatum
- `updated_at`: Aktualisierungsdatum

### Pass
- `pass_id`: Eindeutige Pass-ID
- `pass_type`: 'blank' oder 'longterm'
- `nfc_id`: NFC-Chip-ID
- `qr_code`: QR-Code-Wert
- `is_assigned`: Zugewiesen an Besucher
- `assigned_to`: Besucher-ID (wenn zugewiesen)
- `valid_from`: Gültig ab (optional)
- `valid_until`: Gültig bis (optional)
- `is_active`: Aktiv

### Check-in/out-Datensatz / Check-in/out Record
- `record_id`: Eindeutige Datensatz-ID
- `visitor_id`: Besucher-ID
- `pass_id`: Verwendete Pass-ID
- `action`: 'checkin' oder 'checkout'
- `timestamp`: Zeitstempel
- `method`: 'nfc' oder 'qr'
- `location`: Standort (optional)
- `notes`: Notizen (optional)

---

## 🛠️ Entwicklung / Development

### Lokale Entwicklung / Local Development

```bash
# Mit Auto-Reload starten / Start with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Code-Struktur / Code Structure

Das Projekt folgt dem **Service-Repository-Pattern**:
The project follows the **Service-Repository Pattern**:

- **Models**: Definieren Datenstrukturen / Define data structures
- **Services**: Enthalten Geschäftslogik / Contain business logic
- **Routers**: Definieren API-Endpunkte / Define API endpoints
- **Database**: Verwaltet Datenbankverbindungen / Manages database connections

---

## 📝 Lizenz / License

MIT License - siehe LICENSE-Datei für Details
MIT License - see LICENSE file for details

---

## 🤝 Beitragen / Contributing

Beiträge sind willkommen! Bitte erstellen Sie einen Pull Request.
Contributions are welcome! Please create a pull request.

---

## 📞 Support

Bei Fragen oder Problemen erstellen Sie bitte ein Issue im Repository.
For questions or issues, please create an issue in the repository.

---

**Version**: 1.0.0  
**Erstellt**: 2025  
**Sprache**: Python 3.8+
