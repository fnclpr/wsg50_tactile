/*
    ROS2 node to combine wrenches of fingers

    Copyright 2018-2025 Università della Campania Luigi Vanvitelli

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
#include <geometry_msgs/msg/wrench_stamped.hpp>
#include <uclv_ros2_interfaces/msg/float64_stamped.hpp>
#include <TooN/TooN.h>

using namespace std;
using namespace TooN;

class CombineWrenchNode : public rclcpp::Node
{
public:
    CombineWrenchNode() : Node("combine_wrench")
    {
        this->declare_parameter<std::string>("wrench0_topic", "wrench0");
        this->declare_parameter<std::string>("wrench1_topic", "wrench1");
        this->declare_parameter<std::string>("distance_topic", "distance");
        this->declare_parameter<std::string>("wrench_out_topic", "total_wrench");
        this->declare_parameter<std::string>("grasp_force_topic", "grasp_force");
        this->declare_parameter<std::string>("tf_prefix", "");
        this->declare_parameter<std::string>("frame_id", "grasp_frame");
        this->declare_parameter<double>("distance_offset", 0.0);

        this->get_parameter("wrench0_topic", topic_0_str);
        this->get_parameter("wrench1_topic", topic_1_str);
        this->get_parameter("distance_topic", topic_distance_str);
        this->get_parameter("wrench_out_topic", out_topic_str);
        this->get_parameter("grasp_force_topic", grasp_force_topic_str);
        this->get_parameter("tf_prefix", tf_prefix);
        this->get_parameter("frame_id", frame_id);
        this->get_parameter("distance_offset", distance_offset);

        e_R_0 = Data(1.0, 0.0, 0.0,
                     0.0, 1.0, 0.0,
                     0.0, 0.0, 1.0);

        e_R_1 = Data(-1.0, 0.0, 0.0,
                     0.0, 1.0, 0.0,
                     0.0, 0.0, -1.0);

        _0_r_e = makeVector(0.0, 0.0, 0.04);
        _1_r_e = makeVector(0.0, 0.0, 0.04);

        subWrench0 = this->create_subscription<geometry_msgs::msg::WrenchStamped>(
            topic_0_str, 1, std::bind(&CombineWrenchNode::readWrench0, this, std::placeholders::_1));
        subWrench1 = this->create_subscription<geometry_msgs::msg::WrenchStamped>(
            topic_1_str, 1, std::bind(&CombineWrenchNode::readWrench1, this, std::placeholders::_1));
        subDistance = this->create_subscription<uclv_ros2_interfaces::msg::Float64Stamped>(
            topic_distance_str, 1, std::bind(&CombineWrenchNode::readDistance, this, std::placeholders::_1));

        pubWrench = this->create_publisher<geometry_msgs::msg::WrenchStamped>(out_topic_str, 1);
        pubGraspForce = this->create_publisher<uclv_ros2_interfaces::msg::Float64Stamped>(grasp_force_topic_str, 1);

        totalWrench_msg.header.frame_id = tf_prefix + frame_id;
    }

private:
    void readWrench0(const geometry_msgs::msg::WrenchStamped::SharedPtr msg)
    {
        fz0 = msg->wrench.force.z;
        trWrench0 = trWrench(msg, e_R_0, _0_r_e);
        updateWrench();
    }

    void readWrench1(const geometry_msgs::msg::WrenchStamped::SharedPtr msg)
    {
        fz1 = msg->wrench.force.z;
        trWrench1 = trWrench(msg, e_R_1, _1_r_e);
        updateWrench();
    }

    void readDistance(const uclv_ros2_interfaces::msg::Float64Stamped::SharedPtr msg)
    {
        double distance = ((msg->data) / 2.0) + distance_offset;
        _0_r_e[2] = distance;
        _1_r_e[2] = distance;
    }

    geometry_msgs::msg::WrenchStamped trWrench(const geometry_msgs::msg::WrenchStamped::SharedPtr msg, const Matrix<3, 3> &R, const Vector<3> &r)
    {
        Vector<3> f;
        f[0] = msg->wrench.force.x;
        f[1] = msg->wrench.force.y;
        f[2] = msg->wrench.force.z;

        Vector<3> m;
        m[0] = msg->wrench.torque.x;
        m[1] = msg->wrench.torque.y;
        m[2] = msg->wrench.torque.z;

        Vector<3> f_tr;
        Vector<3> m_tr;

        f_tr = R * f;
        m_tr = R * m + (-(R * r) ^ f_tr);

        geometry_msgs::msg::WrenchStamped outMsg;

        outMsg.wrench.force.x = f_tr[0];
        outMsg.wrench.force.y = f_tr[1];
        outMsg.wrench.force.z = f_tr[2];

        outMsg.wrench.torque.x = m_tr[0];
        outMsg.wrench.torque.y = m_tr[1];
        outMsg.wrench.torque.z = m_tr[2];

        if (rclcpp::Time(msg->header.stamp) > rclcpp::Time(totalWrench_msg.header.stamp))
            totalWrench_msg.header.stamp = msg->header.stamp;
        else
            totalWrench_msg.header.stamp = rclcpp::Time(totalWrench_msg.header.stamp) + rclcpp::Duration::from_seconds(1.0E-6);

        return outMsg;
    }

    void updateWrench()
    {
        totalWrench_msg.wrench.force.x = trWrench0.wrench.force.x + trWrench1.wrench.force.x;
        totalWrench_msg.wrench.force.y = trWrench0.wrench.force.y + trWrench1.wrench.force.y;
        totalWrench_msg.wrench.force.z = trWrench0.wrench.force.z + trWrench1.wrench.force.z;

        totalWrench_msg.wrench.torque.x = trWrench0.wrench.torque.x + trWrench1.wrench.torque.x;
        totalWrench_msg.wrench.torque.y = trWrench0.wrench.torque.y + trWrench1.wrench.torque.y;
        totalWrench_msg.wrench.torque.z = trWrench0.wrench.torque.z + trWrench1.wrench.torque.z;

        graspFroce_msg.data = 2.0 * std::min(fabs(fz0), fabs(fz1));
        graspFroce_msg.header = totalWrench_msg.header;

        pubWrench->publish(totalWrench_msg);
        pubGraspForce->publish(graspFroce_msg);
    }

    Matrix<3, 3> e_R_0 = Identity, e_R_1 = Identity;
    Vector<3> _0_r_e = Zeros, _1_r_e = Zeros;

    rclcpp::Publisher<geometry_msgs::msg::WrenchStamped>::SharedPtr pubWrench;
    rclcpp::Publisher<uclv_ros2_interfaces::msg::Float64Stamped>::SharedPtr pubGraspForce;

    rclcpp::Subscription<geometry_msgs::msg::WrenchStamped>::SharedPtr subWrench0;
    rclcpp::Subscription<geometry_msgs::msg::WrenchStamped>::SharedPtr subWrench1;
    rclcpp::Subscription<uclv_ros2_interfaces::msg::Float64Stamped>::SharedPtr subDistance;

    geometry_msgs::msg::WrenchStamped totalWrench_msg;
    uclv_ros2_interfaces::msg::Float64Stamped graspFroce_msg;

    geometry_msgs::msg::WrenchStamped trWrench0;
    geometry_msgs::msg::WrenchStamped trWrench1;

    double fz0 = 0.0;
    double fz1 = 0.0;
    double distance_offset;

    std::string topic_0_str;
    std::string topic_1_str;
    std::string topic_distance_str;
    std::string out_topic_str;
    std::string grasp_force_topic_str;
    std::string tf_prefix;
    std::string frame_id;
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<CombineWrenchNode>());
    rclcpp::shutdown();
    return 0;
}