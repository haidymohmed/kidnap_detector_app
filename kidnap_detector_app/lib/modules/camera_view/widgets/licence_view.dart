import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'error_image.dart';

class LicenceWidget extends StatelessWidget {
  final bool licencePlat, isCarImage;
  final String? carImage, licenceImage;
  final double height;
  LicenceWidget({
    Key? key,
    required this.height,
    required this.carImage,
    required this.licencePlat,
    this.licenceImage,
    required this.isCarImage,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        isCarImage == true
            ? displayImage(carImage, 2)
            : Container(
                child: Text(""),
              ),
        carImage == true && licencePlat == true ? Expanded(child: Text("")) : Container(),
        licencePlat == true
            ? displayImage(licenceImage, 1)
            : Container(
                child: Text(""),
              ),
      ],
    );
  }

  displayImage(String? imagec, flex) {
    Uint8List image;
    try {
      image = base64.decode(imagec!);
    } catch (e) {
      return ErrorImage();
    }
    return Expanded(
      flex: flex,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(10),
        child: Container(
          clipBehavior: Clip.antiAliasWithSaveLayer,
          decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(10), boxShadow: [
            BoxShadow(
              color: Colors.grey.withOpacity(0.2),
              spreadRadius: 5,
              blurRadius: 7,
              offset: Offset(0, 3), // changes position of shadow
            ),
          ]),
          height: height,
          margin: EdgeInsets.all(10),
          child: Image.memory(
            image,
            fit: BoxFit.fill,
            errorBuilder: (BuildContext context, Object exception, StackTrace? stackTrace) {
              return ErrorImage();
            },
          ),
        ),
      ),
    );
  }
}
