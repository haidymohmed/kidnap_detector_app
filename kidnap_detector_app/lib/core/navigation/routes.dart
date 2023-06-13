import 'package:flutter_modular/flutter_modular.dart';
import 'package:kidnap_detection_app/core/navigation/routes_names.dart';
import 'package:kidnap_detection_app/modules/camera_view/view/grid_camera_view.dart';
import 'package:kidnap_detection_app/modules/camera_view/view/report_details_screen.dart';
import 'package:modular_interfaces/src/route/modular_arguments.dart' show ModularArguments;

List<ModularRoute> modularRoutes = <ChildRoute<dynamic>>[
  ChildRoute<dynamic>(
    AppRoutes.routes.initScreen,
    child: (_, ModularArguments args) => GridCameraView(),
    transition: TransitionType.fadeIn,
  ),
  ChildRoute<dynamic>(
    AppRoutes.routes.gridCamerView,
    child: (_, ModularArguments args) => GridCameraView(),
    transition: TransitionType.fadeIn,
  ),
  ChildRoute<dynamic>(
    AppRoutes.routes.reportDetails,
    child: (_, ModularArguments args) {
      return ReportDetailsScreen(
        caseNumber: args.data!['case_number'] as int,
      );
    },
    transition: TransitionType.fadeIn,
  ),
];
