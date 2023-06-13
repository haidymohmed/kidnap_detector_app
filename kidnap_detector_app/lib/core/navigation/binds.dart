import 'package:flutter_modular/flutter_modular.dart';
import 'package:kidnap_detection_app/core/constant/constant.dart';
import 'package:modular_interfaces/src/di/injector.dart' show Injector;

final List<Bind<Object>> modularBinds = <Bind<Object>>[
  Bind.singleton((Injector<dynamic> i) => Constant()),
];
