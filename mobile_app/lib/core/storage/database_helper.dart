import 'dart:convert';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart' as p;

class DatabaseHelper {
  static const String _dbName = 'mineguard_offline.db';
  static const int _dbVersion = 1;

  static Database? _database;

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final dbPath = await getDatabasesPath();
    final path = p.join(dbPath, _dbName);

    return await openDatabase(
      path,
      version: _dbVersion,
      onCreate: (db, version) async {
        // 1. Offline Sync Queue (durable queue for zero-loss offline submissions)
        await db.execute('''
          CREATE TABLE offline_sync_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT UNIQUE NOT NULL,
            entity_type TEXT NOT NULL,
            payload TEXT NOT NULL,
            status TEXT NOT NULL, -- DRAFT, READY_TO_SYNC, SYNCING, SYNCED, SYNC_FAILED
            retry_count INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            last_error TEXT
          )
        ''');

        // 2. Cached Statutory Checklists & Templates
        await db.execute('''
          CREATE TABLE cached_templates (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            items_json TEXT NOT NULL
          )
        ''');

        // 3. Local Field Reports
        await db.execute('''
          CREATE TABLE local_field_reports (
            client_id TEXT PRIMARY KEY,
            mine_id TEXT NOT NULL,
            zone_id TEXT,
            category TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            accuracy REAL,
            evidence_urls TEXT,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
          )
        ''');

        // 4. Local Inspections
        await db.execute('''
          CREATE TABLE local_inspections (
            client_id TEXT PRIMARY KEY,
            template_id TEXT NOT NULL,
            mine_id TEXT NOT NULL,
            zone_id TEXT,
            inspector_id TEXT NOT NULL,
            shift TEXT NOT NULL,
            status TEXT NOT NULL,
            score REAL NOT NULL,
            results_json TEXT NOT NULL,
            created_at TEXT NOT NULL
          )
        ''');

        // 5. Local Incidents
        await db.execute('''
          CREATE TABLE local_incidents (
            client_id TEXT PRIMARY KEY,
            mine_id TEXT NOT NULL,
            zone_id TEXT,
            incident_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT NOT NULL,
            location_name TEXT,
            latitude REAL,
            longitude REAL,
            immediate_action TEXT,
            evidence_urls TEXT,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
          )
        ''');
      },
    );
  }

  // --- Queue Operations ---
  Future<int> enqueueItem({
    required String clientId,
    required String entityType,
    required Map<String, dynamic> payload,
  }) async {
    final db = await database;
    return await db.insert(
      'offline_sync_queue',
      {
        'client_id': clientId,
        'entity_type': entityType,
        'payload': jsonEncode(payload),
        'status': 'READY_TO_SYNC',
        'retry_count': 0,
        'created_at': DateTime.now().toIso8601String(),
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<List<Map<String, dynamic>>> getPendingQueueItems() async {
    final db = await database;
    return await db.query(
      'offline_sync_queue',
      where: 'status IN (?, ?, ?)',
      whereArgs: ['READY_TO_SYNC', 'SYNC_FAILED', 'DRAFT'],
      orderBy: 'id ASC',
    );
  }

  Future<int> updateQueueStatus(String clientId, String status, {String? error}) async {
    final db = await database;
    return await db.update(
      'offline_sync_queue',
      {
        'status': status,
        if (error != null) 'last_error': error,
      },
      where: 'client_id = ?',
      whereArgs: [clientId],
    );
  }

  Future<int> getPendingQueueCount() async {
    final db = await database;
    final result = await db.rawQuery(
      'SELECT COUNT(*) as count FROM offline_sync_queue WHERE status IN (?, ?)',
      ['READY_TO_SYNC', 'SYNC_FAILED'],
    );
    return Sqflite.firstIntValue(result) ?? 0;
  }
}
