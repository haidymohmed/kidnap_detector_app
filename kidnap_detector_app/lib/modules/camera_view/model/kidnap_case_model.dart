class KidnapCaseModel {
  bool checked ;
  int caseNumber;
  String cameraId;
  String caseTime;
  String? kidnapVideoLink;
  String? licensePlate;
  String? carImage;
  String? licenseImage;
  bool? involvedPeople;
  int numberOfPersons;
  bool? usedCar;
  String? carNumber;
  List<String> kidnapVideo = <String>[];
  List<String> persons = <String>[];
  List<String> cars = <String>[];

  KidnapCaseModel({
    required this.caseNumber,
    required this.cameraId,
    required this.caseTime,
    this.involvedPeople,
    required this.numberOfPersons,
    this.checked = false,
    this.carNumber,
    this.usedCar,
    this.licensePlate,
  });

  factory KidnapCaseModel.fromJson(Map<String, dynamic> json) {
    return KidnapCaseModel(
      caseNumber: json['Case number'] ?? 0,
      cameraId: json['Cameria ID'] ?? '',
      caseTime: json['time'] ?? '',
      involvedPeople: json['Involved people'] ?? false,
      numberOfPersons: json['number_of_persons'] ?? 0,
      usedCar: json['Used car'] ?? false,
      licensePlate: json['Lisence number'] ?? 'No license plate',
      checked: false
    );
  }
}
