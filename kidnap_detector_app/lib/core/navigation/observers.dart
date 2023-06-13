// flutter_modular observers print route name
import 'dart:developer' as developer;

import 'package:flutter/widgets.dart';

class AppModularObserver extends NavigatorObserver {
  @override
  void didPush(Route<dynamic> route, Route<dynamic>? previousRoute) {
    developer.log(
      'Modular (didPush): URL ==> (${route.settings.name}) --||-- previousRoute ==> ${previousRoute?.settings.name} --||-- args ==> ${route.settings.arguments}',
      name: 'AppModularObserver.didPush',
    );
    super.didPush(route, previousRoute);
  }

  @override
  void didPop(Route<dynamic> route, Route<dynamic>? previousRoute) {
    developer.log(
      'Modular (didPop): URL ==> (${route.settings.name}) --||-- previousRoute ==> ${previousRoute?.settings.name} --||-- args ==> ${route.settings.arguments}',
      name: 'AppModularObserver.didPop',
    );
    super.didPop(route, previousRoute);
  }

  @override
  void didRemove(Route<dynamic> route, Route<dynamic>? previousRoute) {
    developer.log(
      'Modular (didRemove): URL ==> (${route.settings.name}) --||-- previousRoute ==> ${previousRoute?.settings.name} --||-- args ==> ${route.settings.arguments}',
      name: 'AppModularObserver.didRemove',
    );
    super.didRemove(route, previousRoute);
  }

  @override
  void didReplace({Route<dynamic>? newRoute, Route<dynamic>? oldRoute}) {
    developer.log(
      'Modular (didReplace): URL ==> (${newRoute?.settings.name ?? '...'}) --||-- previousRoute ==> ${oldRoute?.settings.name ?? '...'} --||-- args ==> ${newRoute?.settings.arguments ?? '...'}',
      name: 'AppModularObserver.didReplace',
    );
    super.didReplace(newRoute: newRoute, oldRoute: oldRoute);
  }
}
