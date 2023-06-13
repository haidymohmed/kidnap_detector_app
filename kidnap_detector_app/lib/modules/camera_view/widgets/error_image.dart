
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

Widget ErrorImage() {
  return Container(
    child: Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(
          Icons.info,
          size: 40,
        ),
        SizedBox(
          height: 5,
          width: 5,
        ),
        Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "unavailable",
              style: GoogleFonts.acme(),
            ),
            Text(
              "Something went wrong",
              style: GoogleFonts.acme(),
            ),
          ],
        )
      ],
    ),
  );
}