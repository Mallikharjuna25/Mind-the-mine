import 'dart:async';
import 'package:flutter/foundation.dart';
import '../core/network/network_info.dart';

class ConnectivityProvider extends ChangeNotifier {
  final NetworkInfo _networkInfo;
  StreamSubscription<bool>? _subscription;
  bool _isOnline = true;

  ConnectivityProvider([NetworkInfo? networkInfo])
      : _networkInfo = networkInfo ?? NetworkInfo() {
    _init();
  }

  bool get isOnline => _isOnline;

  Future<void> _init() async {
    _isOnline = await _networkInfo.isConnected;
    notifyListeners();
    _subscription = _networkInfo.onConnectivityChanged.listen((online) {
      _isOnline = online;
      notifyListeners();
    });
  }

  // Debug helper to manually simulate network disconnect
  void toggleSimulatedOffline() {
    _isOnline = !_isOnline;
    notifyListeners();
  }

  @override
  void dispose() {
    _subscription?.cancel();
    super.dispose();
  }
}
