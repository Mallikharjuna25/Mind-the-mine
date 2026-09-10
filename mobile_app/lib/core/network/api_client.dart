import 'package:dio/dio.dart';
import '../storage/secure_storage_helper.dart';

class ApiClient {
  static const String defaultBaseUrl = "http://10.0.2.2:8000/api/v1"; // 10.0.2.2 for Android emulator, localhost for web/desktop

  final Dio _dio;
  final SecureStorageHelper _secureStorage;

  ApiClient({String baseUrl = defaultBaseUrl, SecureStorageHelper? secureStorage})
      : _secureStorage = secureStorage ?? SecureStorageHelper(),
        _dio = Dio(BaseOptions(
          baseUrl: baseUrl,
          connectTimeout: const Duration(seconds: 15),
          receiveTimeout: const Duration(seconds: 15),
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
        )) {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _secureStorage.getToken();
        if (token != null && token.isNotEmpty) {
          options.headers['Authorization'] = 'Bearer ';
        }
        return handler.next(options);
      },
      onError: (DioException e, handler) {
        // Logging or refreshing token logic can be added here
        return handler.next(e);
      },
    ));
  }

  Dio get dio => _dio;

  // Generic helpers
  Future<Response> get(String path, {Map<String, dynamic>? queryParameters}) {
    return _dio.get(path, queryParameters: queryParameters);
  }

  Future<Response> post(String path, {dynamic data}) {
    return _dio.post(path, data: data);
  }

  Future<Response> patch(String path, {dynamic data}) {
    return _dio.patch(path, data: data);
  }

  // Upload Evidence (Photo, Audio, Video)
  Future<String?> uploadEvidence(String filePath, String fileName) async {
    try {
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(filePath, filename: fileName),
      });
      final response = await _dio.post('/media/upload', data: formData);
      if (response.statusCode == 200 || response.statusCode == 201) {
        return response.data['url'] as String?;
      }
    } catch (e) {
      // Offline fallback: keep local path
      return filePath;
    }
    return null;
  }
}
