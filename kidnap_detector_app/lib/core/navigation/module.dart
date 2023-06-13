import 'package:flutter_modular/flutter_modular.dart';
import 'package:kidnap_detection_app/core/navigation/binds.dart';
import 'package:kidnap_detection_app/core/navigation/routes.dart';


class AppModule extends Module {
  @override
  List<Bind<Object>> get binds => modularBinds;

  @override
  List<ModularRoute> get routes => modularRoutes;
}
