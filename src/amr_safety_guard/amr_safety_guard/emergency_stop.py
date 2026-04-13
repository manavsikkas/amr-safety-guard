#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import Twist


class MyNode(Node):
    def __init__(self):
        super().__init__('emergency_stop')

        #create and stop the timers
        self.stop_timer = self.create_timer(0.1, self.stop_callback)
        self.resume_timer = self.create_timer(5.0, self.resume_callback)
        self.stop_timer.cancel()
        self.resume_timer.cancel()



        #Subcriber
        self.stop_subscriber = self.create_subscription(
            String,
            '/person_detected',
            self.person_detected_callback,
            10
        )

        #publisher
        self.stop_publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )


    #callback funtions

    def stop_callback(self):
        stop = Twist()
        stop.linear.x = 0.0
        stop.angular.z = 0.0   
        self.stop_publisher.publish(stop)

    def resume_callback(self):
        self.stop_timer.cancel()
        self.resume_timer.cancel()
        self.get_logger().info(f'Person Gone -- Resuming patrol')
    

    def person_detected_callback(self, msg):
        self.get_logger().warn(f'EMERGENCY STOP: {msg.data}')
        self.stop_timer.reset()
        self.resume_timer.reset()
            
def main(args=None):
    rclpy.init(args=args)

    node = MyNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
