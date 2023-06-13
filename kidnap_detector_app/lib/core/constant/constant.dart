import 'package:kidnap_detection_app/modules/camera_view/model/kidnap_case_model.dart';

class Constant {
  Map<int, KidnapCaseModel> kidnapCases = {};
  Map<int, KidnapCaseModel> newCases = {};
  int cameraIdThatHaveCase = 0;

  void Function(void Function())? updateReportList;
  void Function(void Function())? updatedkidnapDetails;
  void Function(void Function())? updatedPerson;
  void Function(void Function())? updatedCars;
  List<void Function(void Function())?> updatedVideoWidget = [];
}

