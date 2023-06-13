import 'dart:async';
import 'dart:convert';
import 'dart:developer' as dev;
import 'dart:io';
import 'dart:typed_data';
import 'package:dio/dio.dart';
import 'package:flutter_modular/flutter_modular.dart';
import 'package:kidnap_detection_app/core/constant/constant.dart';
import 'package:screenshot/screenshot.dart';
import 'package:socket_io_client/socket_io_client.dart' as IO;
import 'package:flutter/material.dart';
import 'package:video_player_win/video_player_win.dart';

class VideoWidget extends StatefulWidget {
  final String videoPath;
  final int videoId;
  final height;
  final double width;
  final bool isFromDetails;

  VideoWidget({
    required this.videoPath,
    required this.videoId,
    required this.width,
    required this.height,
    this.isFromDetails = false,
  });
  @override
  _VideoWidgetState createState() => _VideoWidgetState();
}

class _VideoWidgetState extends State<VideoWidget> {
  WinVideoPlayerController? _controller;
  late IO.Socket socket;
  bool isInitialized = false;
  // final SocketService service = Modular.get<SocketService>();
  final Constant constant = Modular.get<Constant>();
  ScreenshotController screenshotController = ScreenshotController();
  Timer? _timer;
  final double desiredFrameRate = 12;
  Dio dio = Dio();

  @override
  void initState() {
    constant.updatedVideoWidget.add(setState);
    Future.delayed(Duration(milliseconds: 500), () async {
      await initVideo();
    });
    // service.initSocket(context);
    super.initState();
  }

  Future<void> initVideo() async {
    try {
      _controller = await WinVideoPlayerController.file(File(widget.videoPath));
      await _controller!.initialize().then((value) async {
        if (_controller!.value.isInitialized) {
          await _controller!.setLooping(false);

          _controller!.addListener(() async {
            if (isInitialized == false && _controller!.value.isInitialized == true) {
              isInitialized = true;
              await _controller!.setVolume(0.0);
              await _controller!.play();
              setState(() {});
            }
          });
        } else {
          dev.log("video file load failed");
        }
      }).catchError((e) {
        dev.log("controller.initialize() error occurs: $e");
      });
      setState(() {});
    } catch (e) {
      dev.log(e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_controller == null)
      return SizedBox.shrink();
    else
      return Container(
        height: MediaQuery.of(context).size.height / 2 - 40,
        width: MediaQuery.of(context).size.width / 2 - 10,
        padding: EdgeInsets.all(5),
        decoration: BoxDecoration(
          color: constant.cameraIdThatHaveCase == widget.videoId ? Colors.red : Colors.transparent,
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
        child: Stack(
          alignment: Alignment.center,
          children: [
            Screenshot(
              controller: screenshotController,
              child: WinVideoPlayer(_controller!),
            ),
            Center(
              child: InkWell(
                onTap: () {
                  setState(() {
                    if (_controller!.value.isPlaying) {
                      _controller!.pause();
                      _timer?.cancel();
                    } else {
                      _controller!.play();
                      _timer = Timer.periodic(
                        Duration(milliseconds: (1000 / 12).round()),
                        (_) {
                          final position = _controller!.value.position;
                          final duration = _controller!.value.duration;
                          if (position >= duration) {
                            _timer!.cancel();
                          } else {
                            if (!widget.isFromDetails) {
                              sendFrame();
                            }
                          }
                        },
                      );
                    }
                  });
                },
                child: Container(
                  width: 50,
                  height: 50,
                  decoration: BoxDecoration(
                    color: Colors.grey.withOpacity(0.4),
                    borderRadius: BorderRadius.circular(25),
                  ),
                  child: Icon(
                    _controller!.value.isPlaying ? Icons.play_arrow : Icons.pause,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
          ],
        ),
      );
  }

  @override
  void dispose() {
    _controller!.dispose();
    _timer?.cancel();

    super.dispose();
  }

  void sendFrame() async {
    try {
      screenshotController.capture().then((Uint8List? image) async {
        if (image != null) {
          await dio.post(
            'http://127.0.0.1:5000/api/send_frame',
            data: {
              "frame": base64.encode(image),
              "camera_id": widget.videoId,
            },
          );
        }
      }).catchError((onError) {
        dev.log(onError.toString());
      });
    } catch (e) {
      dev.log(e.toString());
    }
  }
}
