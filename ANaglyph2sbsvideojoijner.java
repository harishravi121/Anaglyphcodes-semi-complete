import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

/**
 * A Java utility to overlay two video files with specific color washes using FFmpeg.
 * This class assumes FFmpeg is installed on the system and accessible via the PATH.
 */
public class VideoOverlay {

    /**
     * Overlays two video files, applying a red wash to the first and a cyan wash to the second.
     * The second video will be scaled to half its size and centered on the first video.
     *
     * @param video1Path The file path to the first input video (will have red wash, acts as background).
     * @param video2Path The file path to the second input video (will have cyan wash, acts as overlay).
     * @param outputPath The desired file path for the output overlaid video.
     * @return true if the video overlay process was successful, false otherwise.
     */
    public boolean overlayVideosWithColorWash(String video1Path, String video2Path, String outputPath) {
        // Validate input file paths
        Path path1 = Paths.get(video1Path);
        Path path2 = Paths.get(video2Path);
        Path output = Paths.get(outputPath);

        if (!Files.exists(path1) || !Files.isReadable(path1)) {
            System.err.println("Error: Video 1 file not found or not readable: " + video1Path);
            return false;
        }
        if (!Files.exists(path2) || !Files.isReadable(path2)) {
            System.err.println("Error: Video 2 file not found or not readable: " + video2Path);
            return false;
        }

        // Ensure the output directory exists
        Path outputDir = output.getParent();
        if (outputDir != null && !Files.exists(outputDir)) {
            try {
                Files.createDirectories(outputDir);
            } catch (IOException e) {
                System.err.println("Error creating output directory: " + outputDir + " - " + e.getMessage());
                return false;
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
        List<String> command = new ArrayList<>();
        command.add("ffmpeg");
        command.add("-i");
        command.add(video1Path);
        command.add("-i");
        command.add(video2Path);
        command.add("-filter_complex");
        command.add("[0:v]colorchannelmixer=rr=1.0:gg=0.5:bb=0.5[v0_red];" +
                    "[1:v]colorchannelmixer=rr=0.5:gg=1.0:bb=1.0,scale=iw/2:ih/2[v1_cyan_scaled];" +
                    "[v0_red][v1_cyan_scaled]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2[v_out];" +
                    "[0:a][1:a]amerge=inputs=2[a_out]");
        command.add("-map");
        command.add("[v_out]");
        command.add("-map");
        command.add("[a_out]");
        command.add("-ac");
        command.add("2"); // Ensure stereo audio for the output
        command.add("-y"); // Overwrite output file if it exists
        command.add(outputPath);

        ProcessBuilder processBuilder = new ProcessBuilder(command);
        processBuilder.redirectErrorStream(true); // Redirect error stream to output stream

        System.out.println("Executing FFmpeg command: " + String.join(" ", command));

        try {
            Process process = processBuilder.start();

            // Read the output from the FFmpeg process (for debugging/monitoring)
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    System.out.println("FFmpeg: " + line);
                }
            }

            int exitCode = process.waitFor(); // Wait for the process to complete
            if (exitCode == 0) {
                System.out.println("Video overlay successful! Output: " + outputPath);
                return true;
            } else {
                System.err.println("FFmpeg process exited with error code: " + exitCode);
                return false;
            }

        } catch (IOException | InterruptedException e) {
            System.err.println("Error executing FFmpeg command: " + e.getMessage());
            e.printStackTrace();
            return false;
        }
    }

    public static void main(String[] args) {
        // --- IMPORTANT: Replace these paths with your actual video file paths ---
        String video1 = "path/to/your/video1.mp4"; // e.g., "C:/Users/YourUser/Videos/input1.mp4" or "/home/user/videos/input1.mp4"
        String video2 = "path/to/your/video2.mp4"; // e.g., "C:/Users/YourUser/Videos/input2.mp4" or "/home/user/videos/input2.mp4"
        String output = "path/to/your/output_overlay_washed.mp4"; // e.g., "C:/Users/YourUser/Videos/output_overlay_washed.mp4"

        // Example usage:
        VideoOverlay overlay = new VideoOverlay();
        boolean success = overlay.overlayVideosWithColorWash(video1, video2, output);

        if (success) {
            System.out.println("Process completed successfully.");
        } else {
            System.out.println("Process failed.");
        }
    }
}
