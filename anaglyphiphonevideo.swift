import Foundation
import AVFoundation
import Photos // Optional: For saving to Photos library
import ffmpegkit // Make sure you have integrated mobile-ffmpeg-kit-ios

// MARK: - VideoOverlayDelegate Protocol

/// A delegate protocol to communicate the status of the video overlay operation.
protocol VideoOverlayDelegate: AnyObject {
    /// Called when the video overlay operation is successful.
    /// - Parameter outputPath: The file path of the successfully overlaid video.
    func videoOverlayDidSucceed(outputPath: String)

    /// Called when the video overlay operation fails.
    /// - Parameter errorMessage: A descriptive error message.
    func videoOverlayDidFail(errorMessage: String)

    /// Optional: Called to provide progress updates during the video overlay operation.
    /// - Parameters:
    ///   - time: The current processing time in milliseconds.
    ///   - duration: The total duration of the video (may not always be accurate for complex filters).
    func videoOverlayDidUpdateProgress(time: Int64, duration: Int64)
}

// MARK: - VideoOverlay Class

/// A utility class for iOS to overlay two video files with specific color washes using mobile-ffmpeg-kit-ios.
/// This class assumes mobile-ffmpeg-kit-ios is properly integrated into the iOS project.
class VideoOverlay {

    weak var delegate: VideoOverlayDelegate?

    /// Initializes the VideoOverlay.
    init() {}

    /**
     Overlays two video files, applying a red wash to the first (background) and a cyan wash to the second (overlay).
     The second video will be scaled to half its size and centered on the first video.
     This operation is asynchronous. Results are delivered via the `VideoOverlayDelegate`.

     - Parameters:
       - video1URL: The `URL` for the first input video (background, red washed). This should be a file URL.
       - video2URL: The `URL` for the second input video (overlay, cyan washed, scaled). This should be a file URL.
       - outputFileName: The desired file name for the output overlaid video (e.g., "output_overlay_washed.mp4").
                         The output will be saved in the app's temporary directory.
     */
    func overlayVideosWithColorWash(video1URL: URL, video2URL: URL, outputFileName: String) {

        // Validate input file paths
        guard FileManager.default.fileExists(atPath: video1URL.path) else {
            delegate?.videoOverlayDidFail(errorMessage: "Video 1 file not found: \(video1URL.lastPathComponent)")
            return
        }
        guard FileManager.default.fileExists(atPath: video2URL.path) else {
            delegate?.videoOverlayDidFail(errorMessage: "Video 2 file not found: \(video2URL.lastPathComponent)")
            return
        }

        // Define the output file path in the app's temporary directory
        // This is a good place for temporary files before moving them to a permanent location
        let outputDir = FileManager.default.temporaryDirectory
        let outputPath = outputDir.appendingPathComponent(outputFileName).path

        // Ensure the output directory exists (though temporaryDirectory usually does)
        if !FileManager.default.fileExists(atPath: outputDir.path) {
            do {
                try FileManager.default.createDirectory(at: outputDir, withIntermediateDirectories: true, attributes: nil)
            } catch {
                delegate?.videoOverlayDidFail(errorMessage: "Failed to create output directory: \(error.localizedDescription)")
                return
            }
        }

        // Construct the FFmpeg command for color washing and overlaying
        // -i: Input file
        // -filter_complex: Complex filtergraph for video and audio manipulation
        //   [0:v]colorchannelmixer=rr=1.0:gg=0.5:bb=0.5[v0_red]: Applies a red wash to the first video.
        //     'rr=1.0' keeps red channel at full intensity.
        //     'gg=0.5' and 'bb=0.5' reduce green and blue channels to 50%, tinting the video red.
        //     '[v0_red]' is the label for this filtered video stream.
        //   [1:v]colorchannelmixer=rr=0.5:gg=1.0:bb=1.0,scale=iw/2:ih/2[v1_cyan_scaled]:
        //     Applies a cyan wash to the second video.
        //     'rr=0.5' reduces red channel to 50%.
        //     'gg=1.0' and 'bb=1.0' keep green and blue channels at full intensity, tinting the video cyan.
        //     Then, 'scale=iw/2:ih/2' scales this cyan-washed video to half its original width and height.
        //     '[v1_cyan_scaled]' is the label for this filtered and scaled video stream.
        //   [v0_red][v1_cyan_scaled]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2[v_out]:
        //     Overlays the 'v1_cyan_scaled' video on top of the 'v0_red' video.
        //     'x=(main_w-overlay_w)/2' and 'y=(main_h-overlay_h)/2' calculate the coordinates
        //     to center the 'overlay_video' (v1_cyan_scaled) on the 'main_video' (v0_red).
        //     '[v_out]' is the label for the final output video stream.
        //   [0:a][1:a]amerge=inputs=2[a_out]: Merges audio streams from both inputs.
        //     '[a_out]' is the label for the final output audio stream.
        // -map "[v_out]": Maps the output video stream from the filtergraph.
        // -map "[a_out]": Maps the output audio stream from the filtergraph.
        // -ac 2: Sets audio channels to 2 (stereo) for the merged audio.
        // -y: Overwrite output file without asking if it already exists.
        let ffmpegCommand = String(format:
            "-i \"%@\" -i \"%@\" -filter_complex " +
            "\"[0:v]colorchannelmixer=rr=1.0:gg=0.5:bb=0.5[v0_red];" +
            "[1:v]colorchannelmixer=rr=0.5:gg=1.0:bb=1.0,scale=iw/2:ih/2[v1_cyan_scaled];" +
            "[v0_red][v1_cyan_scaled]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2[v_out];" +
            "[0:a][1:a]amerge=inputs=2[a_out]\" " +
            "-map \"[v_out]\" -map \"[a_out]\" -ac 2 -y \"%@\"",
            video1URL.path, video2URL.path, outputPath
        )

        print("Executing FFmpeg command: \(ffmpegCommand)")

        // Execute the FFmpeg command asynchronously using FFmpeg-Kit
        FFmpegKit.executeAsync(ffmpegCommand, withCallback: { session in
            // This callback runs on a background thread.
            // Dispatch to the main thread if updating UI.
            let returnCode = session?.getReturnCode()

            if ReturnCode.isSuccess(returnCode) {
                print("FFmpeg command executed successfully. Output: \(outputPath)")
                DispatchQueue.main.async {
                    self.delegate?.videoOverlayDidSucceed(outputPath: outputPath)
                }
            } else if ReturnCode.isCancel(returnCode) {
                print("FFmpeg command cancelled.")
                DispatchQueue.main.async {
                    self.delegate?.videoOverlayDidFail(errorMessage: "Operation cancelled.")
                }
            } else {
                let errorMessage = session?.getFailStackTrace() ?? session?.getOutput() ?? "Unknown FFmpeg error."
                print("FFmpeg command failed with state \(session?.getState()?.rawValue ?? -1) and return code \(returnCode?.intValue ?? -1). Error: \(errorMessage)")
                DispatchQueue.main.async {
                    self.delegate?.videoOverlayDidFail(errorMessage: "FFmpeg failed: \(errorMessage)")
                }
            }
        }, withLogCallback: { log in
            // Optional: Handle FFmpeg logs for debugging
            // print("FFmpeg Log: \(log?.getMessage() ?? "")")
        }, withStatisticsCallback: { statistics in
            // Optional: Handle FFmpeg statistics for progress updates
            // let timeInMilliseconds = statistics?.getTime() ?? 0
            // let totalDuration = statistics?.getDuration() ?? 0
            // DispatchQueue.main.async {
            //     self.delegate?.videoOverlayDidUpdateProgress(time: timeInMilliseconds, duration: totalDuration)
            // }
        })
    }
}

// MARK: - Example Usage (e.g., in a ViewController)

/*
// In your ViewController.swift or similar file:

import UIKit
import MobileFFmpeg // Ensure this is imported if using the example directly

class ViewController: UIViewController, VideoOverlayDelegate {

    private var videoOverlay: VideoOverlay?

    override func viewDidLoad() {
        super.viewDidLoad()
        videoOverlay = VideoOverlay()
        videoOverlay?.delegate = self
    }

    // Call this method when you want to start overlaying videos, e.g., from a button tap
    @IBAction func overlayVideosButtonTapped(_ sender: UIButton) {
        // --- IMPORTANT: Replace these URLs with your actual video file URLs ---
        // For demonstration, these might be URLs to videos copied into the app's bundle
        // or fetched from the Photos library.
        // For real-world use, you'd typically get these from a UIImagePickerController
        // or a custom file picker.

        // Example: Using URLs from the app's bundle (for testing)
        // Make sure 'video1.mp4' and 'video2.mp4' are added to your Xcode project
        // and included in the target's 'Copy Bundle Resources'.
        guard let video1URL = Bundle.main.url(forResource: "video1", withExtension: "mp4"),
              let video2URL = Bundle.main.url(forResource: "video2", withExtension: "mp4") else {
            print("Error: Could not find video files in app bundle.")
            return
        }

        // Example: Using URLs from a sandboxed directory (e.g., Documents directory)
        // let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
        // let video1URL = documentsPath.appendingPathComponent("my_video_1.mp4")
        // let video2URL = documentsPath.appendingPathComponent("my_video_2.mp4")

        let outputFileName = "overlayed_washed_video.mp4"

        print("Starting video overlay process...")
        videoOverlay?.overlayVideosWithColorWash(video1URL: video1URL, video2URL: video2URL, outputFileName: outputFileName)
    }

    // MARK: - VideoOverlayDelegate Methods

    func videoOverlayDidSucceed(outputPath: String) {
        print("Video overlay successful! Output path: \(outputPath)")
        // You can now move this file to a permanent location,
        // display it, or save it to the Photos library.
        // Example: Saving to Photos library (requires "Privacy - Photo Library Additions Usage Description" in Info.plist)
        // saveVideoToPhotosLibrary(videoPath: outputPath)
    }

    func videoOverlayDidFail(errorMessage: String) {
        print("Video overlay failed: \(errorMessage)")
        // Show an alert to the user
        let alert = UIAlertController(title: "Error", message: "Video overlay failed: \(errorMessage)", preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default, handler: nil))
        present(alert, animated: true, completion: nil)
    }

    func videoOverlayDidUpdateProgress(time: Int64, duration: Int64) {
        // Update a UIProgressView or similar
        // print("Progress: \(time) / \(duration)")
    }

    // Helper function to save video to Photos Library
    private func saveVideoToPhotosLibrary(videoPath: String) {
        PHPhotoLibrary.shared().performChanges({
            PHAssetChangeRequest.creationRequestForAssetFromVideo(atFileURL: URL(fileURLWithPath: videoPath))
        }) { success, error in
            if success {
                print("Video successfully saved to Photos Library.")
            } else {
                print("Error saving video to Photos Library: \(error?.localizedDescription ?? "Unknown error")")
            }
        }
    }
}
*/
