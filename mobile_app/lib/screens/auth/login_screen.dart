import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../../providers/auth_provider.dart';
import '../home/dashboard_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _userIdController = TextEditingController(text: 'INSP-DHANBAD-05');
  final _passwordController = TextEditingController(text: 'password123');
  String _selectedMine = 'MINE-DHANBAD-01';
  String _selectedRole = 'INSPECTOR';

  final List<String> _mines = [
    'MINE-DHANBAD-01',
    'MINE-KORBA-02',
    'MINE-SINGRAULI-03',
    'MINE-NCL-DUDHICHUA-04',
  ];

  final List<String> _roles = [
    'INSPECTOR',
    'SAFETY_OFFICER',
    'ENVIRONMENT_OFFICER',
    'MINE_MANAGER',
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Logo & Header
                Container(
                  width: 64,
                  height: 64,
                  decoration: BoxDecoration(
                    color: AppColors.safetyOrange.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: AppColors.safetyOrange, width: 1.5),
                  ),
                  child: const Icon(Icons.shield, color: AppColors.safetyOrange, size: 36),
                ),
                const SizedBox(height: 16),
                const Text(
                  'AI MINEGUARD',
                  style: TextStyle(
                    color: AppColors.textPrimary,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1.2,
                  ),
                ),
                const SizedBox(height: 4),
                const Text(
                  'Module 2: Field Inspector & Mobile Reporting',
                  style: TextStyle(color: AppColors.textSecondary, fontSize: 13),
                ),
                const SizedBox(height: 32),

                // Form
                TextField(
                  controller: _userIdController,
                  decoration: const InputDecoration(
                    labelText: 'Officer / Inspector ID',
                    prefixIcon: Icon(Icons.badge, color: AppColors.safetyOrange),
                  ),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _passwordController,
                  obscureText: true,
                  decoration: const InputDecoration(
                    labelText: 'Secure Password / PIN',
                    prefixIcon: Icon(Icons.lock, color: AppColors.safetyOrange),
                  ),
                ),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  value: _selectedMine,
                  decoration: const InputDecoration(
                    labelText: 'Active Mine Site',
                    prefixIcon: Icon(Icons.location_city, color: AppColors.safetyOrange),
                  ),
                  dropdownColor: AppColors.surface,
                  items: _mines.map((m) => DropdownMenuItem(value: m, child: Text(m))).toList(),
                  onChanged: (val) {
                    if (val != null) setState(() => _selectedMine = val);
                  },
                ),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  value: _selectedRole,
                  decoration: const InputDecoration(
                    labelText: 'Officer Role',
                    prefixIcon: Icon(Icons.engineering, color: AppColors.safetyOrange),
                  ),
                  dropdownColor: AppColors.surface,
                  items: _roles.map((r) => DropdownMenuItem(value: r, child: Text(r))).toList(),
                  onChanged: (val) {
                    if (val != null) setState(() => _selectedRole = val);
                  },
                ),
                const SizedBox(height: 28),

                ElevatedButton.icon(
                  onPressed: () async {
                    final auth = context.read<AuthProvider>();
                    auth.switchRole(_selectedRole);
                    await auth.login(_userIdController.text, _passwordController.text, _selectedMine);
                    if (mounted) {
                      Navigator.pushReplacement(
                        context,
                        MaterialPageRoute(builder: (_) => const DashboardScreen()),
                      );
                    }
                  },
                  icon: const Icon(Icons.login),
                  label: const Text('AUTHENTICATE & ENTER PIT'),
                ),
                const SizedBox(height: 16),
                const Text(
                  'Offline-first security enabled: Session authenticated with hardware JWT keychain.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: AppColors.textMuted, fontSize: 11),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
