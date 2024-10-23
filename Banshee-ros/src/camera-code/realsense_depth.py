import cv2
import pyrealsense2 as rs
import numpy as np

class DepthCamera:
    #set the resolution of the regular camera and the depth sensing camera
    DEPTH_WIDTH = 848
    DEPTH_HEIGHT = 480
    COLOR_WIDTH = 848
    COLOR_HEIGHT = 480

    def __init__(self):
        # Configure depth, color, and infrared streams
        self.pipeline = rs.pipeline()
        config = rs.config()

        #turn on camera using width and height
        config.enable_stream(rs.stream.depth, self.DEPTH_WIDTH, self.DEPTH_HEIGHT, rs.format.z16, 60)
        config.enable_stream(rs.stream.color, self.COLOR_WIDTH, self.COLOR_HEIGHT, rs.format.bgr8, 60)

        # Start the pipeline and get the active profile
        self.pipeline.start(config)

        # Additional settings for autoexposure
        #sensor = profile.get_device().first_color_sensor()
        #sensor.set_option(rs.option.enable_auto_exposure, 1)

        self.align = rs.align(rs.stream.color)

    def get_frame(self):
        #set frames of camera
        frames = self.pipeline.wait_for_frames()
        # set frames to alight with camera
        aligned_frames = self.align.process(frames)
        #copy the aligned frames to depth sensing camera and color camera
        aligned_depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if not aligned_depth_frame or not color_frame:
            return False, None, None, None, None
        #post processing to allow spatial resolution
        dtd_depth = self.dtd(aligned_depth_frame)
        filtered_depth = self.spatial(dtd_depth)


        depth_image = np.asanyarray(dtd_depth.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        return True, depth_image, color_image

    def release(self):
        self.pipeline.stop()
    #function to use a spatial filter post processing to clear image
    def spatial(self, depth_frame):
        spatial = rs.spatial_filter()
        spatial.set_option(rs.option.filter_magnitude, 2)
        spatial.set_option(rs.option.filter_smooth_alpha, 0.25)
        spatial.set_option(rs.option.filter_smooth_delta, 20)
        return spatial.process(depth_frame)
    #function to allow depth to disparity post processing to clear image
    def dtd(self, depth_frame):
        depth_to_disparity = rs.disparity_transform(False)
        return depth_to_disparity.process(depth_frame)

if __name__ == "__main__":
    dc = DepthCamera()
    while True:
        ret, depth_frame, color_frame= dc.get_frame()
        if not ret:
            break

        normalized_depth = cv2.normalize(depth_frame, None, 0, 255, cv2.NORM_MINMAX)
        normalized_depth = np.uint8(normalized_depth)
        colored_depth = cv2.applyColorMap(normalized_depth, cv2.COLORMAP_JET)
        alpha = 0.7
        # overlap depth sensing map with regular color map
        overlay = cv2.addWeighted(color_frame, 1 - alpha, colored_depth, alpha, 0)
        # show distance in regular camera 
        cv2.imshow("Depth Overlaid on Color", overlay)

        key = cv2.waitKey(1)
        if key == 27:
            break

    dc.release()
    cv2.destroyAllWindows()
