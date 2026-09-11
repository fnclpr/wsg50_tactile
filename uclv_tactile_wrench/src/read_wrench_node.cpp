// filepath: /home/mcostanzo/rosws/tactile-ws/src/uclv_tactile_wrench/src/read_wrench_node.cpp
/*
    ROS2 node to calculate wrenches

    Copyright 2018-2025 Università della Campania Luigi Vanvitelli

    Author: Marco Costanzo <marco.costanzo@unicampania.it>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>
#include <geometry_msgs/msg/wrench_stamped.hpp>
#include <uclv_tactile_interfaces/msg/tactile_stamped.hpp>

#include <stdio.h>
#include <iostream>

#include <ANN/ANN_File_Reader.h>

using namespace std;
using namespace TooN;

class ReadWrenchNode : public rclcpp::Node
{
public:
    ReadWrenchNode() : Node("read_wrench")
    {
        this->declare_parameter<std::string>("finger_calibration_file", "");
        this->declare_parameter<std::string>("in_voltage_topic", "tactile_voltage/rect");
        this->declare_parameter<std::string>("wrench_topic", "wrench");

        this->get_parameter("finger_calibration_file", finger_calibration_file);
        this->get_parameter("in_voltage_topic", in_voltage_topic_str);
        this->get_parameter("wrench_topic", wrench_topic_str);

        if (finger_calibration_file.empty())
        {
            RCLCPP_ERROR(this->get_logger(), "Error! - No params for 'finger_calibration_file' - stopping node...");
            rclcpp::shutdown();
            return;
        }

        RCLCPP_INFO(this->get_logger(), "Finger file %s", finger_calibration_file.c_str());

        pubWrench = this->create_publisher<geometry_msgs::msg::WrenchStamped>(wrench_topic_str, 1);
        subVoltage = this->create_subscription<uclv_tactile_interfaces::msg::TactileStamped>(
            in_voltage_topic_str, 1, std::bind(&ReadWrenchNode::readV, this, std::placeholders::_1));

        init_model();
    }

private:
    void readV(const uclv_tactile_interfaces::msg::TactileStamped::ConstSharedPtr& msg)
    {
        for (int i = 0; i < NUM_V; i++)
        {
            voltages[i] = msg->tactile.data[i];
        }

        wrench = ann->compute(voltages);

        msgWrench.header.stamp = msg->header.stamp;
        msgWrench.header.frame_id = msg->header.frame_id;
        msgWrench.wrench.force.x = wrench[0];
        msgWrench.wrench.force.y = wrench[1];
        msgWrench.wrench.force.z = wrench[2];
        msgWrench.wrench.torque.x = wrench[3];
        msgWrench.wrench.torque.y = wrench[4];
        msgWrench.wrench.torque.z = wrench[5];

        pubWrench->publish(msgWrench);
    }

    void init_model()
    {
        ann = std::make_unique<ANN>(readANNFile(finger_calibration_file));
        RCLCPP_INFO(this->get_logger(), "ANN Model");
        RCLCPP_INFO(this->get_logger(), "Model initialized!");
    }

    static const int NUM_V = 25;
    Vector<NUM_V> voltages = Zeros;
    Vector<6> wrench = Zeros;
    std::string finger_calibration_file;
    std::unique_ptr<ANN> ann;
    std::string in_voltage_topic_str;
    std::string wrench_topic_str;

    rclcpp::Publisher<geometry_msgs::msg::WrenchStamped>::SharedPtr pubWrench;
    rclcpp::Subscription<uclv_tactile_interfaces::msg::TactileStamped>::SharedPtr subVoltage;
    geometry_msgs::msg::WrenchStamped msgWrench;
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<ReadWrenchNode>());
    rclcpp::shutdown();
    return 0;
}