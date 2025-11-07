# Systemarchitektur - Besucherverwaltungssystem
# System Architecture - Visitor Management System

---

## 📐 Architekturübersicht / Architecture Overview

### Deutsch

Das Besucherverwaltungssystem folgt einer **mehrschichtigen Architektur** (Layered Architecture) mit klarer Trennung von Verantwortlichkeiten. Die Anwendung basiert auf dem **Service-Repository-Pattern** und verwendet **FastAPI** als Web-Framework.

### English

The Visitor Management System follows a **layered architecture** with clear separation of concerns. The application is based on the **Service-Repository Pattern** and uses **FastAPI** as the web framework.

---

## 🏗️ Schichtenmodell / Layer Model

```
┌─────────────────────────────────────────────────────────┐
│                    Präsentationsschicht                  │
│                   Presentation Layer                     │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Web UI (HTML/CSS/JavaScript)                    │    │
│  │  - Besucher-Registrierung / Visitor Registration│    │
│  │  - Check-in/Check-out Interface                  │    │
│  │  - Anwesenheitsübersicht / Presence Overview     │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────┐
│                      API-Schicht                         │
│                      API Layer                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │  FastAPI Routers                                 │    │
│  │  - /visitors (Besucher-Endpunkte)              │    │
│  │  - /passes (Pass-Endpunkte)                     │    │
│  │  - /checkinout (Check-in/out-Endpunkte)        │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────┐
│                   Geschäftslogik-Schicht                 │
│                   Business Logic Layer                   │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Services                                        │    │
│  │  - VisitorService                               │    │
│  │  - PassService                                   │    │
│  │  - CheckInOutService                            │    │
│  │  - CloudSyncService                             │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────┐
│                   Datenzugriffsschicht                   │
│                   Data Access Layer                      │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Database (MongoDB)                              │    │
│  │  - visitors_collection                           │    │
│  │  - passes_collection                             │    │
│  │  - checkinout_collection                        │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────┐
│                   External Services                      │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Cloud Storage (für Feuerwehr-Compliance)       │    │
│  │  - Anwesenheitsdatei / Presence File            │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Komponentendiagramm / Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │    Visitors    │  │     Passes     │  │  CheckInOut  │  │
│  │     Router     │  │     Router     │  │    Router    │  │
│  └────────┬───────┘  └────────┬───────┘  └──────┬───────┘  │
│           │                    │                  │          │
│           ▼                    ▼                  ▼          │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │    Visitor     │  │      Pass      │  │  CheckInOut  │  │
│  │    Service     │  │    Service     │  │   Service    │  │
│  └────────┬───────┘  └────────┬───────┘  └──────┬───────┘  │
│           │                    │                  │          │
│           └────────────────────┴──────────────────┘          │
│                              │                                │
│                              ▼                                │
│                    ┌───────────────────┐                     │
│                    │   MongoDB Client  │                     │
│                    └─────────┬─────────┘                     │
│                              │                                │
│  ┌───────────────────────────┼───────────────────────────┐  │
│  │                           ▼                            │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐    │  │
│  │  │ Visitors │  │  Passes  │  │    CheckInOut    │    │  │
│  │  │Collection│  │Collection│  │    Collection    │    │  │
│  │  └──────────┘  └──────────┘  └──────────────────┘    │  │
│  │                    MongoDB Database                   │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │             CloudSyncService                          │  │
│  │  ┌──────────────────────────────────────────────┐    │  │
│  │  │  Synchronisiert Anwesenheitsdaten            │    │  │
│  │  │  Synchronizes presence data                  │    │  │
│  │  └──────────────────────────────────────────────┘    │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │   Cloud Storage      │
                │  (Presence File)     │
                └──────────────────────┘
```

---

## 🔄 Datenfluss / Data Flow

### Besucher-Registrierung / Visitor Registration

```
1. Client
   └─> POST /visitors/register
       └─> Visitors Router
           └─> Pass validieren / Validate pass
               └─> Pass Service
                   └─> MongoDB (passes_collection)
           └─> Besucher erstellen / Create visitor
               └─> Visitor Service
                   └─> MongoDB (visitors_collection)
           └─> Pass zuweisen / Assign pass
               └─> Pass Service
                   └─> MongoDB (passes_collection UPDATE)
           └─> Response zurück / Return response
```

### Check-in Prozess / Check-in Process

```
1. Client (NFC/QR Scanner)
   └─> POST /checkinout/checkin
       └─> CheckInOut Router
           └─> Check-in durchführen / Perform check-in
               └─> CheckInOut Service
                   ├─> Besucher finden / Find visitor
                   │   └─> Visitor Service
                   │       └─> MongoDB (visitors_collection)
                   ├─> Check-in-Datensatz erstellen
                   │   └─> MongoDB (checkinout_collection)
                   └─> Besucherstatus aktualisieren
                       └─> Visitor Service
                           └─> MongoDB (visitors_collection UPDATE)
           └─> Anwesenheitsbericht generieren
               └─> CheckInOut Service
                   └─> MongoDB (visitors_collection QUERY)
           └─> Cloud synchronisieren
               └─> Cloud Sync Service
                   └─> Cloud Storage (JSON-Datei)
           └─> Response zurück
```

### Check-out Prozess / Check-out Process

```
1. Client (NFC/QR Scanner)
   └─> POST /checkinout/checkout
       └─> CheckInOut Router
           └─> Check-out durchführen / Perform check-out
               └─> CheckInOut Service
                   ├─> Besucher finden / Find visitor
                   │   └─> Visitor Service
                   │       └─> MongoDB (visitors_collection)
                   ├─> Check-out-Datensatz erstellen
                   │   └─> MongoDB (checkinout_collection)
                   └─> Besucherstatus aktualisieren
                       └─> Visitor Service
                           └─> MongoDB (visitors_collection UPDATE)
           └─> Anwesenheitsbericht generieren
               └─> CheckInOut Service
                   └─> MongoDB (visitors_collection QUERY)
           └─> Cloud synchronisieren
               └─> Cloud Sync Service
                   └─> Cloud Storage (JSON-Datei)
           └─> Response zurück
```

---

## 🎯 Design Patterns

### 1. Service Layer Pattern
- **Zweck**: Kapselung der Geschäftslogik
- **Implementation**: Separate Service-Klassen für jede Domäne
- **Vorteile**: 
  - Wiederverwendbarkeit
  - Testbarkeit
  - Klare Trennung von API und Logik

### 2. Repository Pattern
- **Zweck**: Abstrahierung des Datenzugriffs
- **Implementation**: Services greifen über MongoDB Collections zu
- **Vorteile**:
  - Datenbankänderungen isoliert
  - Einfaches Testen mit Mock-Daten

### 3. Dependency Injection
- **Zweck**: Lose Kopplung zwischen Komponenten
- **Implementation**: Services erhalten Collections als Parameter
- **Vorteile**:
  - Bessere Testbarkeit
  - Flexibilität bei der Konfiguration

---

## 💾 Datenmodell / Data Model

### Entity-Relationship Diagram

```
┌─────────────────────────────────────────────────────────┐
│                          Pass                            │
├─────────────────────────────────────────────────────────┤
│ PK: pass_id (String)                                    │
│     pass_type (String: 'blank'|'longterm')              │
│     nfc_id (String?)                                    │
│     qr_code (String?)                                   │
│     is_assigned (Boolean)                               │
│     assigned_to (String?)                               │
│     valid_from (DateTime?)                              │
│     valid_until (DateTime?)                             │
│     is_active (Boolean)                                 │
│     created_at (DateTime)                               │
│     updated_at (DateTime)                               │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ 1:1
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                        Visitor                           │
├─────────────────────────────────────────────────────────┤
│ PK: visitor_id (String)                                 │
│     first_name (String)                                 │
│     last_name (String)                                  │
│     email (String)                                      │
│     phone (String?)                                     │
│     company (String?)                                   │
│ FK: pass_id (String) → Pass.pass_id                     │
│     pass_type (String)                                  │
│     is_active (Boolean)                                 │
│     created_at (DateTime)                               │
│     updated_at (DateTime)                               │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ 1:N
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                      CheckInOut                          │
├─────────────────────────────────────────────────────────┤
│ PK: record_id (String)                                  │
│ FK: visitor_id (String) → Visitor.visitor_id            │
│ FK: pass_id (String) → Pass.pass_id                     │
│     action (String: 'checkin'|'checkout')               │
│     timestamp (DateTime)                                │
│     method (String: 'nfc'|'qr')                         │
│     location (String?)                                  │
│     notes (String?)                                     │
└─────────────────────────────────────────────────────────┘
```

---

## 🔐 Sicherheitsarchitektur / Security Architecture

### 1. Validierung / Validation
- **Pydantic Models**: Automatische Datenvalidierung
- **Pass-Validierung**: Prüfung auf Gültigkeit vor Verwendung
- **Eindeutigkeits-Constraints**: E-Mail, Pass-ID, NFC-ID, QR-Code

### 2. Datenintegrität / Data Integrity
- **Transaktionen**: Atomare Operationen für Check-in/out
- **Zeitstempel**: Alle Aktionen werden protokolliert
- **Status-Tracking**: Konsistente Verfolgung der Besucheranwesenheit

### 3. Cloud-Synchronisation / Cloud Synchronization
- **Automatisch**: Bei jeder Statusänderung
- **UTF-8 Encoding**: Für internationale Zeichen
- **JSON Format**: Standardisiertes Datenformat
- **Fehlerbehandlung**: Robuste Error-Handling

---

## 📊 Skalierbarkeit / Scalability

### Horizontale Skalierung / Horizontal Scaling
- **FastAPI**: Asynchrone Request-Verarbeitung
- **MongoDB**: Sharding-Unterstützung
- **Stateless API**: Einfaches Load-Balancing

### Vertikale Skalierung / Vertical Scaling
- **Indizes**: Optimierte Datenbankabfragen
- **Caching**: Möglichkeit für Redis-Integration
- **Connection Pooling**: Effiziente Datenbankverbindungen

---

## 🔄 API-Design Principles

### RESTful Endpoints
- **Ressourcen-orientiert**: /visitors, /passes, /checkinout
- **HTTP-Verben**: GET, POST, PUT, DELETE
- **Status-Codes**: Korrekte HTTP-Statuscodes
- **JSON-Format**: Standardisiertes Datenformat

### Dokumentation
- **OpenAPI (Swagger)**: Automatische API-Dokumentation
- **Beispiele**: Code-Beispiele in Dokumentation
- **Typisierung**: Vollständige Type-Hints

---

## 🌐 Cloud-Integration / Cloud Integration

### Aktuell / Current
- **Lokale Simulation**: JSON-Datei im Dateisystem
- **Automatische Updates**: Bei Check-in/out

### Produktions-Integration / Production Integration
Für die Produktion kann der `CloudSyncService` erweitert werden für:

- **AWS S3**: 
  ```python
  import boto3
  s3 = boto3.client('s3')
  s3.put_object(Bucket='bucket', Key='presence.json', Body=json_data)
  ```

- **Azure Blob Storage**:
  ```python
  from azure.storage.blob import BlobServiceClient
  blob_client.upload_blob(data)
  ```

- **Google Cloud Storage**:
  ```python
  from google.cloud import storage
  bucket.blob('presence.json').upload_from_string(data)
  ```

---

## 📈 Performance-Überlegungen / Performance Considerations

### Datenbank-Indizes / Database Indexes
- `visitors.email` (Unique)
- `visitors.pass_id` (Unique)
- `visitors.is_active` (für Anwesenheitsabfragen)
- `passes.nfc_id` (Unique, für schnelle NFC-Suche)
- `passes.qr_code` (Unique, für schnelle QR-Suche)
- `checkinout.timestamp` (für Zeitbereichsabfragen)
- `checkinout.visitor_id` (für Besucherhistorie)

### Caching-Strategien / Caching Strategies
- **Anwesenheitsliste**: Cache für 30 Sekunden
- **Pass-Validierung**: Cache für 5 Minuten
- **Statistiken**: Cache für 1 Minute

---

## 🧪 Testing-Architektur / Testing Architecture

### Unit Tests
- **Service-Tests**: Isolierte Tests für jede Service-Klasse
- **Mock-Datenbank**: Verwendung von Mock-Collections
- **Edge Cases**: Fehlerbehandlung und Grenzfälle

### Integration Tests
- **API-Tests**: End-to-End-Tests für alle Endpunkte
- **Datenbank-Tests**: Tests mit echter MongoDB-Instanz
- **Workflow-Tests**: Komplette User-Journeys

### Test-Umgebung / Test Environment
```bash
# Test mit pytest
pytest tests/

# Mit Coverage
pytest --cov=backend tests/
```

---

## 🔧 Erweiterbarkeit / Extensibility

### Geplante Features / Planned Features
1. **Multi-Standort-Unterstützung**: Mehrere Gebäude/Eingänge
2. **Besucher-Kategorien**: Verschiedene Zugriffsberechtigungen
3. **Zeitbasierte Beschränkungen**: Besuchszeiten
4. **Benachrichtigungen**: E-Mail/SMS bei Check-in/out
5. **Reporting**: Erweiterte Analyse und Berichte
6. **Mobile App**: Native iOS/Android-Apps

### Plugin-Architektur
- **Event-System**: Hooks für Check-in/out-Events
- **Custom-Services**: Erweiterbare Service-Schicht
- **Middleware**: Custom-Middleware für FastAPI

---

## 📝 Zusammenfassung / Summary

### Stärken / Strengths
✅ Klare Trennung der Verantwortlichkeiten  
✅ Skalierbare Architektur  
✅ Erweiterbar und wartbar  
✅ Gut dokumentiert  
✅ RESTful API-Design  
✅ Automatische Cloud-Synchronisation  

### Verbesserungspotenzial / Areas for Improvement
🔄 Authentifizierung und Autorisierung  
🔄 Rate Limiting  
🔄 Erweiterte Fehlerbehandlung  
🔄 Monitoring und Logging  
🔄 Performance-Optimierungen  
🔄 Echte Cloud-Integration  

---

**Version**: 1.0.0  
**Letzte Aktualisierung / Last Updated**: 2025  
**Autor / Author**: System Architecture Team
