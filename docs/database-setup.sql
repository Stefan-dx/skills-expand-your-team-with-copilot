-- ============================================================================
-- Besucherverwaltungssystem - Datenbank Setup Script
-- Visitor Management System - Database Setup Script
-- ============================================================================
-- Dieses SQL-Script erstellt die notwendige Datenbankstruktur für ein
-- Besucherverwaltungssystem mit Microsoft SQL Server Express.
--
-- This SQL script creates the necessary database structure for a
-- visitor management system with Microsoft SQL Server Express.
-- ============================================================================

-- Datenbank erstellen (falls nicht vorhanden)
-- Create database (if not exists)
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'VisitorManagement')
BEGIN
    CREATE DATABASE VisitorManagement;
END
GO

USE VisitorManagement;
GO

-- ============================================================================
-- TABELLE: Passes (Pässe)
-- TABLE: Passes
-- ============================================================================
-- Speichert Informationen über Besucher-Pässe (NFC und QR-Codes)
-- Stores information about visitor passes (NFC and QR codes)

IF OBJECT_ID('dbo.Passes', 'U') IS NOT NULL
    DROP TABLE dbo.Passes;
GO

CREATE TABLE dbo.Passes (
    PassID NVARCHAR(50) PRIMARY KEY,
    PassType NVARCHAR(20) NOT NULL CHECK (PassType IN ('blank', 'longterm')),
    NFCID NVARCHAR(100) NULL,
    QRCode NVARCHAR(100) NULL,
    IsAssigned BIT NOT NULL DEFAULT 0,
    AssignedTo NVARCHAR(50) NULL,
    ValidFrom DATETIME2 NULL,
    ValidUntil DATETIME2 NULL,
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    
    -- Eindeutige Constraints
    CONSTRAINT UQ_Passes_NFCID UNIQUE (NFCID),
    CONSTRAINT UQ_Passes_QRCode UNIQUE (QRCode)
);
GO

-- Index für schnelle Suche nach NFC und QR
-- Index for fast NFC and QR lookup
CREATE NONCLUSTERED INDEX IX_Passes_NFCID ON dbo.Passes(NFCID) WHERE NFCID IS NOT NULL;
CREATE NONCLUSTERED INDEX IX_Passes_QRCode ON dbo.Passes(QRCode) WHERE QRCode IS NOT NULL;
CREATE NONCLUSTERED INDEX IX_Passes_PassType ON dbo.Passes(PassType);
GO

-- ============================================================================
-- TABELLE: Visitors (Besucher)
-- TABLE: Visitors
-- ============================================================================
-- Speichert Informationen über registrierte Besucher
-- Stores information about registered visitors

IF OBJECT_ID('dbo.Visitors', 'U') IS NOT NULL
    DROP TABLE dbo.Visitors;
GO

CREATE TABLE dbo.Visitors (
    VisitorID NVARCHAR(50) PRIMARY KEY,
    FirstName NVARCHAR(100) NOT NULL,
    LastName NVARCHAR(100) NOT NULL,
    Email NVARCHAR(255) NOT NULL,
    Phone NVARCHAR(50) NULL,
    Company NVARCHAR(255) NULL,
    PassID NVARCHAR(50) NOT NULL,
    PassType NVARCHAR(20) NOT NULL,
    IsActive BIT NOT NULL DEFAULT 0,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    
    -- Foreign Key zu Passes
    CONSTRAINT FK_Visitors_Passes FOREIGN KEY (PassID) REFERENCES dbo.Passes(PassID),
    
    -- Eindeutige Constraints
    CONSTRAINT UQ_Visitors_Email UNIQUE (Email),
    CONSTRAINT UQ_Visitors_PassID UNIQUE (PassID)
);
GO

-- Indizes für häufige Suchen
-- Indexes for frequent searches
CREATE NONCLUSTERED INDEX IX_Visitors_Email ON dbo.Visitors(Email);
CREATE NONCLUSTERED INDEX IX_Visitors_LastName ON dbo.Visitors(LastName);
CREATE NONCLUSTERED INDEX IX_Visitors_Company ON dbo.Visitors(Company);
CREATE NONCLUSTERED INDEX IX_Visitors_IsActive ON dbo.Visitors(IsActive);
GO

-- ============================================================================
-- TABELLE: CheckInOut (Check-in/Check-out Datensätze)
-- TABLE: CheckInOut (Check-in/Check-out Records)
-- ============================================================================
-- Speichert alle Check-in und Check-out Vorgänge
-- Stores all check-in and check-out operations

IF OBJECT_ID('dbo.CheckInOut', 'U') IS NOT NULL
    DROP TABLE dbo.CheckInOut;
GO

CREATE TABLE dbo.CheckInOut (
    RecordID NVARCHAR(50) PRIMARY KEY,
    VisitorID NVARCHAR(50) NOT NULL,
    PassID NVARCHAR(50) NOT NULL,
    Action NVARCHAR(20) NOT NULL CHECK (Action IN ('checkin', 'checkout')),
    Timestamp DATETIME2 NOT NULL DEFAULT GETDATE(),
    Method NVARCHAR(10) NOT NULL CHECK (Method IN ('nfc', 'qr')),
    Location NVARCHAR(255) NULL,
    Notes NVARCHAR(MAX) NULL,
    
    -- Foreign Keys
    CONSTRAINT FK_CheckInOut_Visitors FOREIGN KEY (VisitorID) REFERENCES dbo.Visitors(VisitorID),
    CONSTRAINT FK_CheckInOut_Passes FOREIGN KEY (PassID) REFERENCES dbo.Passes(PassID)
);
GO

-- Indizes für Zeitbereichsabfragen und Besucherhistorie
-- Indexes for time range queries and visitor history
CREATE NONCLUSTERED INDEX IX_CheckInOut_Timestamp ON dbo.CheckInOut(Timestamp DESC);
CREATE NONCLUSTERED INDEX IX_CheckInOut_VisitorID ON dbo.CheckInOut(VisitorID, Timestamp DESC);
CREATE NONCLUSTERED INDEX IX_CheckInOut_Action ON dbo.CheckInOut(Action, Timestamp DESC);
GO

-- ============================================================================
-- TABELLE: CloudSyncLog (Cloud-Synchronisations-Log)
-- TABLE: CloudSyncLog
-- ============================================================================
-- Protokolliert Cloud-Synchronisationsvorgänge
-- Logs cloud synchronization operations

IF OBJECT_ID('dbo.CloudSyncLog', 'U') IS NOT NULL
    DROP TABLE dbo.CloudSyncLog;
GO

CREATE TABLE dbo.CloudSyncLog (
    SyncID INT IDENTITY(1,1) PRIMARY KEY,
    SyncTimestamp DATETIME2 NOT NULL DEFAULT GETDATE(),
    TotalPresent INT NOT NULL,
    SyncStatus NVARCHAR(20) NOT NULL CHECK (SyncStatus IN ('success', 'failed', 'pending')),
    ErrorMessage NVARCHAR(MAX) NULL,
    CloudFileURL NVARCHAR(500) NULL
);
GO

-- Index für Zeitabfragen
-- Index for time queries
CREATE NONCLUSTERED INDEX IX_CloudSyncLog_Timestamp ON dbo.CloudSyncLog(SyncTimestamp DESC);
GO

-- ============================================================================
-- VIEWS (Ansichten für häufige Abfragen)
-- VIEWS (Views for common queries)
-- ============================================================================

-- Aktuelle Anwesenheit / Current Presence
IF OBJECT_ID('dbo.vw_CurrentPresence', 'V') IS NOT NULL
    DROP VIEW dbo.vw_CurrentPresence;
GO

CREATE VIEW dbo.vw_CurrentPresence AS
SELECT 
    v.VisitorID,
    v.FirstName,
    v.LastName,
    v.Email,
    v.Company,
    v.PassID,
    v.PassType,
    (SELECT TOP 1 Timestamp 
     FROM dbo.CheckInOut 
     WHERE VisitorID = v.VisitorID AND Action = 'checkin'
     ORDER BY Timestamp DESC) AS LastCheckIn
FROM dbo.Visitors v
WHERE v.IsActive = 1;
GO

-- Besucherhistorie / Visitor History
IF OBJECT_ID('dbo.vw_VisitorHistory', 'V') IS NOT NULL
    DROP VIEW dbo.vw_VisitorHistory;
GO

CREATE VIEW dbo.vw_VisitorHistory AS
SELECT 
    cio.RecordID,
    cio.VisitorID,
    v.FirstName,
    v.LastName,
    v.Email,
    v.Company,
    cio.PassID,
    cio.Action,
    cio.Timestamp,
    cio.Method,
    cio.Location,
    cio.Notes
FROM dbo.CheckInOut cio
INNER JOIN dbo.Visitors v ON cio.VisitorID = v.VisitorID;
GO

-- Verfügbare Pässe / Available Passes
IF OBJECT_ID('dbo.vw_AvailablePasses', 'V') IS NOT NULL
    DROP VIEW dbo.vw_AvailablePasses;
GO

CREATE VIEW dbo.vw_AvailablePasses AS
SELECT 
    PassID,
    PassType,
    NFCID,
    QRCode,
    ValidFrom,
    ValidUntil
FROM dbo.Passes
WHERE IsAssigned = 0 
  AND IsActive = 1
  AND (ValidFrom IS NULL OR ValidFrom <= GETDATE())
  AND (ValidUntil IS NULL OR ValidUntil >= GETDATE());
GO

-- ============================================================================
-- STORED PROCEDURES (Gespeicherte Prozeduren)
-- STORED PROCEDURES
-- ============================================================================

-- Prozedur: Check-in durchführen / Procedure: Perform Check-in
IF OBJECT_ID('dbo.sp_CheckIn', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_CheckIn;
GO

CREATE PROCEDURE dbo.sp_CheckIn
    @PassID NVARCHAR(50),
    @Method NVARCHAR(10),
    @Location NVARCHAR(255) = NULL,
    @Notes NVARCHAR(MAX) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @VisitorID NVARCHAR(50);
    DECLARE @RecordID NVARCHAR(50);
    DECLARE @ErrorMessage NVARCHAR(500);
    
    -- Besucher anhand Pass-ID finden
    SELECT @VisitorID = VisitorID
    FROM dbo.Visitors
    WHERE PassID = @PassID;
    
    -- Prüfen ob Besucher existiert
    IF @VisitorID IS NULL
    BEGIN
        SET @ErrorMessage = 'Kein Besucher für Pass ' + @PassID + ' gefunden / No visitor found for pass ' + @PassID;
        THROW 50001, @ErrorMessage, 1;
        RETURN;
    END
    
    -- Prüfen ob bereits eingecheckt
    DECLARE @IsActive BIT;
    SELECT @IsActive = IsActive FROM dbo.Visitors WHERE VisitorID = @VisitorID;
    
    IF @IsActive = 1
    BEGIN
        SET @ErrorMessage = 'Besucher ist bereits eingecheckt / Visitor is already checked in';
        THROW 50002, @ErrorMessage, 1;
        RETURN;
    END
    
    BEGIN TRANSACTION;
    
    TRY
        -- Check-in-Datensatz erstellen
        SET @RecordID = 'record_' + CONVERT(NVARCHAR(50), NEWID());
        
        INSERT INTO dbo.CheckInOut (RecordID, VisitorID, PassID, Action, Timestamp, Method, Location, Notes)
        VALUES (@RecordID, @VisitorID, @PassID, 'checkin', GETDATE(), @Method, @Location, @Notes);
        
        -- Besucherstatus aktualisieren
        UPDATE dbo.Visitors
        SET IsActive = 1, UpdatedAt = GETDATE()
        WHERE VisitorID = @VisitorID;
        
        COMMIT TRANSACTION;
        
        -- Erfolg zurückgeben
        SELECT 
            @RecordID AS RecordID,
            @VisitorID AS VisitorID,
            'Check-in erfolgreich / Check-in successful' AS Message;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

-- Prozedur: Check-out durchführen / Procedure: Perform Check-out
IF OBJECT_ID('dbo.sp_CheckOut', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_CheckOut;
GO

CREATE PROCEDURE dbo.sp_CheckOut
    @PassID NVARCHAR(50),
    @Method NVARCHAR(10),
    @Location NVARCHAR(255) = NULL,
    @Notes NVARCHAR(MAX) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @VisitorID NVARCHAR(50);
    DECLARE @RecordID NVARCHAR(50);
    DECLARE @ErrorMessage NVARCHAR(500);
    
    -- Besucher anhand Pass-ID finden
    SELECT @VisitorID = VisitorID
    FROM dbo.Visitors
    WHERE PassID = @PassID;
    
    -- Prüfen ob Besucher existiert
    IF @VisitorID IS NULL
    BEGIN
        SET @ErrorMessage = 'Kein Besucher für Pass ' + @PassID + ' gefunden / No visitor found for pass ' + @PassID;
        THROW 50001, @ErrorMessage, 1;
        RETURN;
    END
    
    -- Prüfen ob eingecheckt
    DECLARE @IsActive BIT;
    SELECT @IsActive = IsActive FROM dbo.Visitors WHERE VisitorID = @VisitorID;
    
    IF @IsActive = 0
    BEGIN
        SET @ErrorMessage = 'Besucher ist nicht eingecheckt / Visitor is not checked in';
        THROW 50003, @ErrorMessage, 1;
        RETURN;
    END
    
    BEGIN TRANSACTION;
    
    TRY
        -- Check-out-Datensatz erstellen
        SET @RecordID = 'record_' + CONVERT(NVARCHAR(50), NEWID());
        
        INSERT INTO dbo.CheckInOut (RecordID, VisitorID, PassID, Action, Timestamp, Method, Location, Notes)
        VALUES (@RecordID, @VisitorID, @PassID, 'checkout', GETDATE(), @Method, @Location, @Notes);
        
        -- Besucherstatus aktualisieren
        UPDATE dbo.Visitors
        SET IsActive = 0, UpdatedAt = GETDATE()
        WHERE VisitorID = @VisitorID;
        
        COMMIT TRANSACTION;
        
        -- Erfolg zurückgeben
        SELECT 
            @RecordID AS RecordID,
            @VisitorID AS VisitorID,
            'Check-out erfolgreich / Check-out successful' AS Message;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

-- Prozedur: Anwesenheitsbericht generieren / Procedure: Generate Presence Report
IF OBJECT_ID('dbo.sp_GeneratePresenceReport', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_GeneratePresenceReport;
GO

CREATE PROCEDURE dbo.sp_GeneratePresenceReport
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        COUNT(*) AS TotalPresent,
        GETDATE() AS ReportTimestamp
    FROM dbo.Visitors
    WHERE IsActive = 1;
    
    SELECT * FROM dbo.vw_CurrentPresence
    ORDER BY LastCheckIn DESC;
END
GO

-- ============================================================================
-- INITIAL DATA (Initiale Testdaten)
-- INITIAL DATA
-- ============================================================================

-- Blanko-Pässe erstellen / Create Blank Passes
INSERT INTO dbo.Passes (PassID, PassType, NFCID, QRCode, IsAssigned, IsActive, CreatedAt, UpdatedAt)
VALUES 
    ('BLANK-001', 'blank', '04:1A:2B:3C:4D:5E', 'VIS-BLANK-001', 0, 1, GETDATE(), GETDATE()),
    ('BLANK-002', 'blank', '04:2B:3C:4D:5E:6F', 'VIS-BLANK-002', 0, 1, GETDATE(), GETDATE()),
    ('BLANK-003', 'blank', '04:3C:4D:5E:6F:7A', 'VIS-BLANK-003', 0, 1, GETDATE(), GETDATE());
GO

-- Langzeitpässe erstellen / Create Long-term Passes
INSERT INTO dbo.Passes (PassID, PassType, NFCID, QRCode, IsAssigned, IsActive, CreatedAt, UpdatedAt)
VALUES 
    ('LONGTERM-001', 'longterm', '04:5E:A2:3A:1B:80', 'VIS-LT-001', 0, 1, GETDATE(), GETDATE()),
    ('LONGTERM-002', 'longterm', '04:6F:B3:4B:2C:91', 'VIS-LT-002', 0, 1, GETDATE(), GETDATE());
GO

-- ============================================================================
-- TRIGGERS (Trigger für automatische Updates)
-- TRIGGERS (Triggers for automatic updates)
-- ============================================================================

-- Trigger: UpdatedAt automatisch aktualisieren / Trigger: Auto-update UpdatedAt
IF OBJECT_ID('dbo.tr_Visitors_UpdatedAt', 'TR') IS NOT NULL
    DROP TRIGGER dbo.tr_Visitors_UpdatedAt;
GO

CREATE TRIGGER dbo.tr_Visitors_UpdatedAt
ON dbo.Visitors
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    UPDATE dbo.Visitors
    SET UpdatedAt = GETDATE()
    FROM dbo.Visitors v
    INNER JOIN inserted i ON v.VisitorID = i.VisitorID;
END
GO

-- Trigger: UpdatedAt für Passes / Trigger: UpdatedAt for Passes
IF OBJECT_ID('dbo.tr_Passes_UpdatedAt', 'TR') IS NOT NULL
    DROP TRIGGER dbo.tr_Passes_UpdatedAt;
GO

CREATE TRIGGER dbo.tr_Passes_UpdatedAt
ON dbo.Passes
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    UPDATE dbo.Passes
    SET UpdatedAt = GETDATE()
    FROM dbo.Passes p
    INNER JOIN inserted i ON p.PassID = i.PassID;
END
GO

-- ============================================================================
-- BERECHTIGUNGEN (Permissions - Optional)
-- PERMISSIONS (Optional)
-- ============================================================================

-- Beispiel: Benutzer für die Anwendung erstellen
-- Example: Create user for the application
-- HINWEIS: Passen Sie Benutzername und Passwort an!
-- NOTE: Adjust username and password!

/*
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'VisitorAppUser')
BEGIN
    CREATE LOGIN VisitorAppUser WITH PASSWORD = 'SecurePassword123!';
END
GO

USE VisitorManagement;
GO

IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'VisitorAppUser')
BEGIN
    CREATE USER VisitorAppUser FOR LOGIN VisitorAppUser;
END
GO

-- Berechtigungen erteilen / Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Visitors TO VisitorAppUser;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.Passes TO VisitorAppUser;
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.CheckInOut TO VisitorAppUser;
GRANT SELECT, INSERT ON dbo.CloudSyncLog TO VisitorAppUser;
GRANT SELECT ON dbo.vw_CurrentPresence TO VisitorAppUser;
GRANT SELECT ON dbo.vw_VisitorHistory TO VisitorAppUser;
GRANT SELECT ON dbo.vw_AvailablePasses TO VisitorAppUser;
GRANT EXECUTE ON dbo.sp_CheckIn TO VisitorAppUser;
GRANT EXECUTE ON dbo.sp_CheckOut TO VisitorAppUser;
GRANT EXECUTE ON dbo.sp_GeneratePresenceReport TO VisitorAppUser;
GO
*/

-- ============================================================================
-- FERTIG! / DONE!
-- ============================================================================

PRINT '============================================================================';
PRINT 'Datenbank-Setup abgeschlossen! / Database setup completed!';
PRINT '============================================================================';
PRINT '';
PRINT 'Erstellt / Created:';
PRINT '- 4 Tabellen / 4 Tables (Passes, Visitors, CheckInOut, CloudSyncLog)';
PRINT '- 3 Views (vw_CurrentPresence, vw_VisitorHistory, vw_AvailablePasses)';
PRINT '- 3 Stored Procedures (sp_CheckIn, sp_CheckOut, sp_GeneratePresenceReport)';
PRINT '- 2 Triggers (tr_Visitors_UpdatedAt, tr_Passes_UpdatedAt)';
PRINT '- 5 Testpässe / 5 Test Passes (3 Blanko, 2 Langzeit)';
PRINT '';
PRINT 'Nächste Schritte / Next Steps:';
PRINT '1. Passen Sie ggf. Berechtigungen an / Adjust permissions if needed';
PRINT '2. Konfigurieren Sie die Anwendungsverbindung / Configure application connection';
PRINT '3. Testen Sie die Stored Procedures / Test the stored procedures';
PRINT '';
PRINT '============================================================================';
GO
