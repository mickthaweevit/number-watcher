# Import Logging System Documentation

## **Overview**
Complete tracking system for all import operations with status monitoring, history management, and error handling.

## **Database Schema**

### **ImportLog Table**
```sql
CREATE TABLE import_logs (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255),              -- "backup-2025-06-27.json"
    import_type VARCHAR(50) NOT NULL,   -- "backup", "date_range", "sample_data"
    started_at TIMESTAMP DEFAULT NOW(), -- When import started
    completed_at TIMESTAMP,             -- When import finished (NULL if running)
    status VARCHAR(20) DEFAULT 'running', -- "running", "success", "failed"
    records_processed INTEGER DEFAULT 0, -- Number of records processed
    games_created INTEGER DEFAULT 0,    -- Games created
    results_created INTEGER DEFAULT 0,  -- Results created
    error_message TEXT,                 -- Error details if failed
    file_size BIGINT                    -- File size in bytes
);
```

## **API Endpoints**

### **Get Import Logs**
```bash
GET /import-logs
# Returns last 20 import logs ordered by started_at DESC
```

### **Clear Import Logs**
```bash
DELETE /import-logs
# Clears all import log history
# Returns count of deleted logs
```

## **Import Types**

### **Sample Data Import**
- **Type**: `sample_data`
- **Filename**: `responseData.json`
- **Trigger**: Manual via API endpoint
- **Tracking**: Records processed, games created, results updated

### **Backup Import**
- **Type**: `backup`
- **Filename**: User-provided (e.g., `numwatch-backup-2025-06-27.json`)
- **Trigger**: File upload via frontend
- **Tracking**: File size, games created, results created

### **Date Range Import**
- **Type**: `date_range`
- **Filename**: `null` (API-based)
- **Trigger**: Scheduler service
- **Tracking**: Date range, successful dates, failed dates

## **Status Flow**

### **Import Lifecycle**
```
1. Import starts → Log created with status "running"
2. Processing → Records counted and tracked
3. Success → Status updated to "success", completed_at set
4. Failure → Status updated to "failed", error_message set
```

### **Status Types**
- **running**: Import in progress
- **success**: Import completed successfully
- **failed**: Import encountered errors

## **Frontend Integration**

### **Import Logs Table**
- **Location**: Scheduler page
- **Columns**: Filename, Type, Started, Status, Records, Games, Results
- **Features**: 
  - Color-coded status (Green/Red/Blue)
  - Auto-refresh every 10 seconds
  - Shows latest 20 imports
  - Clear logs functionality

### **Status Colors**
```css
.success { background: green-100, color: green-800 }
.failed  { background: red-100, color: red-800 }
.running { background: blue-100, color: blue-800 }
```

### **Auto-refresh Logic**
```javascript
// Refresh logs every 10 seconds when on scheduler page
onMounted(() => {
  fetchImportLogs()
  logsIntervalId = setInterval(fetchImportLogs, 10000)
})

// Clean up interval when leaving page
onUnmounted(() => {
  if (logsIntervalId) {
    clearInterval(logsIntervalId)
  }
})
```

## **Error Handling**

### **Backend Error Capture**
```python
try:
    # Import operation
    result = process_import()
    
    # Update log with success
    import_log.status = "success"
    import_log.completed_at = datetime.now()
    import_log.games_created = result.games_created
    
except Exception as e:
    # Update log with failure
    import_log.status = "failed"
    import_log.completed_at = datetime.now()
    import_log.error_message = str(e)
```

### **Frontend Error Display**
- Failed imports show in red
- Error messages available in backend logs
- User sees failed status immediately

## **Integration Points**

### **Sample Data Import**
```python
@app.post("/import-sample-data")
async def import_sample_data(db: Session = Depends(get_db)):
    # Create log entry
    import_log = ImportLog(
        filename="responseData.json",
        import_type="sample_data",
        status="running"
    )
    db.add(import_log)
    db.flush()
    
    try:
        # Process import...
        # Update log with success
    except Exception as e:
        # Update log with failure
```

### **Backup Import**
```python
@app.post("/import-backup")
async def import_backup(backup_data: dict, db: Session = Depends(get_db)):
    # Extract metadata
    metadata = backup_data.get("_metadata", {})
    filename = metadata.get("filename")
    file_size = metadata.get("file_size")
    
    # Create log entry with metadata
    import_log = ImportLog(
        filename=filename,
        import_type="backup",
        status="running",
        file_size=file_size
    )
```

### **Frontend File Upload**
```javascript
const handleFileImport = async (event) => {
  const file = event.target.files[0]
  
  // Add metadata to backup data
  backupData._metadata = {
    filename: file.name,
    file_size: file.size
  }
  
  // Import and refresh logs
  await gameApi.importBackup(backupData)
  await fetchImportLogs()
}
```

## **Monitoring & Maintenance**

### **Log Cleanup**
- **Manual**: Clear logs button with confirmation
- **Automatic**: Could implement retention policy (e.g., keep 30 days)

### **Performance Considerations**
- **Limit**: Show only last 20 logs
- **Indexing**: Index on started_at for efficient sorting
- **Cleanup**: Regular cleanup of old logs to prevent table growth

### **Monitoring Queries**
```sql
-- Check recent import status
SELECT import_type, status, COUNT(*) 
FROM import_logs 
WHERE started_at > NOW() - INTERVAL '24 hours'
GROUP BY import_type, status;

-- Find failed imports
SELECT * FROM import_logs 
WHERE status = 'failed' 
ORDER BY started_at DESC 
LIMIT 10;

-- Calculate success rate
SELECT 
  import_type,
  COUNT(*) as total,
  SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
  ROUND(100.0 * SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM import_logs 
GROUP BY import_type;
```

## **Benefits**

### **Operational**
- **Visibility**: See all import operations and their status
- **Debugging**: Error messages help troubleshoot issues
- **History**: Track import patterns and success rates

### **User Experience**
- **Confidence**: Users know if imports completed successfully
- **Transparency**: Clear status even if browser closed during import
- **Recovery**: Can identify and retry failed imports

### **Development**
- **Monitoring**: Track system health and import performance
- **Analytics**: Understand usage patterns
- **Maintenance**: Identify recurring issues