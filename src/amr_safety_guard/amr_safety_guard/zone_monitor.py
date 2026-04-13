#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from std_msgs.msg import String


class MyNode(Node):
    def __init__(self):
        super().__init__('zone_monitor')

        #create publisher
        self.alert_pub = self.create_publisher(
            String,
            '/zone_alert',
            10
        )



        #create subscriber
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

    def odom_callback(self, msg):
        #position
        x=msg.pose.pose.position.x
        y=msg.pose.pose.position.y

        if x >= 4.0 and x <= 8.0 and y >= -3.0 and y <= 3.0:
            self.get_logger().info('Danger Zone')
            alert = String()
            alert.data = f'DANGER: Robot in zone at x={x:.2f}, y={y:.2f}'
            self.alert_pub.publish(alert)



def main(args=None):
    rclpy.init(args=args)

    node = MyNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()