import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_modular/flutter_modular.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:kidnap_detection_app/core/constant/constant.dart';
import 'package:kidnap_detection_app/modules/camera_view/widgets/error_image.dart';

class PersonsDetails extends StatefulWidget {
  final int caseNumber;
  const PersonsDetails({
    super.key,
    required this.caseNumber,
  });

  @override
  State<PersonsDetails> createState() => _PersonsDetailsState();
}

class _PersonsDetailsState extends State<PersonsDetails> {
  // final SocketService sNavigation = Modular.get<SocketService>();
  final Constant constant = Modular.get<Constant>();

  @override
  void initState() {
    constant.updatedPerson = setState;
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Expanded(
      flex: 3,
      child: Container(
        child: SizedBox(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.start,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: Text(
                  "Persons",
                  style: GoogleFonts.acme(fontSize: 20),
                ),
              ),
              Expanded(
                child: SingleChildScrollView(
                  child: LayoutBuilder(
                    builder: (context, constrains) {
                      return Wrap(
                        alignment: WrapAlignment.center,
                        direction: Axis.horizontal,
                        spacing: 5,
                        runSpacing: 5,
                        runAlignment: WrapAlignment.spaceAround,
                        children: constant.kidnapCases[widget.caseNumber]!.persons.map((e) {
                          Uint8List image;
                          try {
                            image = base64.decode(e);
                          } catch (e) {
                            return SizedBox.shrink();
                          }
                          return ClipRRect(
                            borderRadius: BorderRadius.circular(10),
                            child: Container(
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(10),
                                boxShadow: [
                                  BoxShadow(
                                    color: Colors.grey.withOpacity(0.2),
                                    spreadRadius: 5,
                                    blurRadius: 7,
                                    offset: Offset(0, 3), // changes position of shadow
                                  ),
                                ],
                              ),
                              child: Image.memory(
                                image,
                                errorBuilder: (BuildContext context, Object exception, StackTrace? stackTrace) {
                                  return ErrorImage();
                                },
                              ),
                            ),
                          );
                        }).toList(),
                      );
                    },
                  ),
                ),
              )
            ],
          ),
        ),
      ),
    );
  }
}
