#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO


class DetectorNode(Node):
    def __init__(self):
        super().__init__('person_detector')
        self.bridge = CvBridge()
        self.model = YOLO('yolov8n.pt')


        #subscriber
        self.image_subscriber = self.create_subscription(
            Image,
            '/image_raw',
            self.image_callback,
            10
        )

        #publisher
        self.alerter = self.create_publisher(
            String,
            '/person_detected',
            10
        )

    def image_callback(self, msg):
        cv_image= self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        results = self.model(cv_image)
        for box in results[0].boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            if cls == 0 and conf > 0.5:
                alert = String()
                alert.data = f'Human detected: {conf:.2f}'
                self.get_logger().info(f'Person Detected: {conf:.2f}', throttle_duration_sec = 5.0)
                self.alerter.publish(alert)

def main(args=None):
    rclpy.init(args=args)

    node = DetectorNode()

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
    