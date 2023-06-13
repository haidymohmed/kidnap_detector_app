import 'dart:async';
import 'dart:io';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_modular/flutter_modular.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:kidnap_detection_app/core/constant/constant.dart';
import 'package:kidnap_detection_app/modules/camera_view/widgets/persons_details.dart';
import '../widgets/cushtom_button.dart';
import '../widgets/licence_view.dart';
import '../widgets/video_widget.dart';

class ReportDetailsScreen extends StatefulWidget {
  ReportDetailsScreen({
    super.key,
    required this.caseNumber,
  });

  final int caseNumber;

  @override
  _ReportDetailsScreenState createState() => _ReportDetailsScreenState();
}

class _ReportDetailsScreenState extends State<ReportDetailsScreen> {
  final Constant constant = Modular.get<Constant>();
  bool person = false, licencePlat = false, carImage = false;
  @override
  void initState() {
    super.initState();
    constant.updatedkidnapDetails = setState;
    Future.delayed(Duration.zero, () {
      getPesons();
      getKidnapVideo();
    });

    if(constant.newCases.containsKey(widget.caseNumber)){
      constant.newCases.remove(widget.caseNumber);
    }
  }

  void getPesons() async {
    constant.kidnapCases[widget.caseNumber]?.persons.clear();
    Dio dio = Dio();
    Response response = await dio.get(
      "http://127.0.0.1:5000/api/get_persons",
      queryParameters: {
        "case_number": widget.caseNumber,
      },
    );
    response.data['result'].forEach((element) {
      constant.kidnapCases[widget.caseNumber]?.persons.add(element);
    });
  }

  void getKidnapVideo() async {
    Dio dio = Dio();

    try {
      Response response = await dio.get(
        "http://127.0.0.1:5000/api/get_kidnap_video",
        queryParameters: {
          "case_number": widget.caseNumber,
        },
        options: Options(
          responseType: ResponseType.bytes,
        ),
      );
      String localVideoPath = 'assets/cases/video_${widget.caseNumber}.mp4';
      await File(localVideoPath).writeAsBytes(response.data);
      setState(() {
        constant.kidnapCases[widget.caseNumber]?.kidnapVideoLink = localVideoPath;
      });
    } catch (e) {}
  }

  int framNumber = 0;
  @override
  Widget build(BuildContext context) {
    if (framNumber == 0) {
      if (constant.kidnapCases[widget.caseNumber]?.kidnapVideo.isNotEmpty ?? false) {
        Timer.periodic(
          Duration(milliseconds: 50),
          (timer) {
            if ((constant.kidnapCases[widget.caseNumber]?.kidnapVideo.length ?? 0) - 1 == framNumber) {
              timer.cancel();
            } else {
              setState(() {
                framNumber++;
              });
            }
          },
        );
      }
    }
    return Scaffold(
      appBar: AppBar(
        title: Text('Kidnap case ${widget.caseNumber}'),
      ),
      body: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          Expanded(
            flex: 4,
            child: Center(
              child: Container(
                width: MediaQuery.of(context).size.width / 1.5,
                child: SingleChildScrollView(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.start,
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      getCart(
                        leading: "Camera Id : ${constant.kidnapCases[widget.caseNumber]?.cameraId}",
                        trailing: constant.kidnapCases[widget.caseNumber]!.caseTime.toString(),
                      ),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Container(
                            width: MediaQuery.of(context).size.width / 2.5,
                            height: MediaQuery.of(context).size.height / 2,
                            margin: EdgeInsets.symmetric(horizontal: 5, vertical: 5),
                            padding: EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                            decoration:
                                BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(10), boxShadow: [
                              BoxShadow(
                                color: Colors.grey.withOpacity(0.2),
                                spreadRadius: 5,
                                blurRadius: 7,
                                offset: Offset(0, 3), // changes position of shadow
                              ),
                            ]),
                            child: /*constant.kidnapCases[widget.caseNumber]?.kidnapVideo.isEmpty ?? false ?
                            Center(
                                child: CircularProgressIndicator(
                                )
                            )
                                :
                                */
                                SizedBox(
                              width: MediaQuery.of(context).size.width * 0.7,
                              child: VideoWidget(
                                isFromDetails: true,
                                videoPath: constant.kidnapCases[widget.caseNumber]!.kidnapVideoLink.toString(),
                                videoId: 5,
                                height: MediaQuery.of(context).size.height / 3,
                                width: MediaQuery.of(context).size.width / 3,
                              ),
                            ),
                          ),
                          Expanded(
                            child: Container(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                crossAxisAlignment: CrossAxisAlignment.center,
                                children: [
                                  CustomButton(
                                    title: "Play Video",
                                    onTap: () {
                                      getKidnapVideo();
                                      setState(() {});
                                    },
                                  ),
                                  CustomButton(
                                    title: "Show Persons",
                                    onTap: () {
                                      setState(() {
                                        person = true;
                                      });
                                    },
                                  ),
                                  CustomButton(
                                    title: "Show Licence number",
                                    onTap: () async {
                                      try {
                                        Dio dio = Dio();
                                        Response response = await dio.get(
                                          "http://127.0.0.1:5000/api/get_licence",
                                          queryParameters: {
                                            "case_number": widget.caseNumber,
                                          },
                                        );
                                        constant.kidnapCases[widget.caseNumber]?.licenseImage = response.data['result'];
                                      } catch (e) {}
                                      setState(() {
                                        licencePlat = true;
                                      });
                                    },
                                  ),
                                  CustomButton(
                                    title: "Show car",
                                    onTap: () async {
                                      try {
                                        Dio dio = Dio();
                                        Response response = await dio.get(
                                          "http://127.0.0.1:5000/api/get_used_car",
                                          queryParameters: {
                                            "case_number": widget.caseNumber,
                                          },
                                        );
                                        constant.kidnapCases[widget.caseNumber]?.carImage = response.data['result'];
                                      } catch (e) {}
                                      setState(() {
                                        carImage = true;
                                      });
                                    },
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
                      carImage == true || licencePlat == true ? Divider() : Container(),
                      getCart(
                        leading: "Licence Number",
                        trailing: constant.kidnapCases[widget.caseNumber]!.licensePlate.toString(),
                      ),
                      carImage == true || licencePlat == true
                          ? LicenceWidget(
                              isCarImage: carImage,
                              licencePlat: licencePlat,
                              carImage: constant.kidnapCases[widget.caseNumber]!.carImage,
                              licenceImage: constant.kidnapCases[widget.caseNumber]!.licenseImage,
                              height: MediaQuery.of(context).size.height / 4,
                            )
                          : Container(),
                    ],
                  ),
                ),
              ),
            ),
          ),
          person == true ? VerticalDivider() : Container(),
          person == true ? PersonsDetails(caseNumber: widget.caseNumber) : Container(),
        ],
      ),
    );
  }

  getCart({required String leading, required String trailing}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Padding(
          padding: const EdgeInsets.all(8.0),
          child: Text(
            leading,
            style: GoogleFonts.acme(fontSize: 20),
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(8.0),
          child: Text(
            trailing,
            style: GoogleFonts.acme(fontSize: 20),
          ),
        ),
      ],
    );
  }
}
