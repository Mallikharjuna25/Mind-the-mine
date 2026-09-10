import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/constants/app_theme.dart';
import 'core/network/api_client.dart';
import 'core/network/network_info.dart';
import 'core/storage/database_helper.dart';
import 'core/storage/secure_storage_helper.dart';
import 'core/sync/sync_engine.dart';
import 'data/repositories/offline_first_repository.dart';
import 'providers/auth_provider.dart';
import 'providers/connectivity_provider.dart';
import 'providers/sync_provider.dart';
import 'providers/inspection_provider.dart';
import 'providers/incident_provider.dart';
import 'providers/field_report_provider.dart';
import 'providers/verification_provider.dart';
import 'screens/auth/login_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  // Core singletons
  final networkInfo = NetworkInfo();
  final secureStorage = SecureStorageHelper();
  final dbHelper = DatabaseHelper();
  final apiClient = ApiClient(secureStorage: secureStorage);
  final syncEngine = SyncEngine(
    networkInfo: networkInfo,
    apiClient: apiClient,
    dbHelper: dbHelper,
    secureStorage: secureStorage,
  );
  final repository = OfflineFirstRepository(
    apiClient: apiClient,
    dbHelper: dbHelper,
    networkInfo: networkInfo,
    syncEngine: syncEngine,
  );

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider(secureStorage)),
        ChangeNotifierProvider(create: (_) => ConnectivityProvider(networkInfo)),
        ChangeNotifierProvider(create: (_) => SyncProvider(syncEngine)),
        ChangeNotifierProvider(create: (_) => InspectionProvider(repository)),
        ChangeNotifierProvider(create: (_) => IncidentProvider(repository)),
        ChangeNotifierProvider(create: (_) => FieldReportProvider(repository)),
        ChangeNotifierProvider(create: (_) => VerificationProvider(repository)),
      ],
      child: const MineGuardFieldApp(),
    ),
  );
}

class MineGuardFieldApp extends StatelessWidget {
  const MineGuardFieldApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI MineGuard - Module 2 Field Inspector',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: const LoginScreen(),
    );
  }
}
