#include <chrono>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

using namespace std::chrono_literals;

/**
 * Simple Publisher Node in C++
 * Publishes "Hello World" messages to /chatter topic
 */
class SimplePublisher : public rclcpp::Node
{
public:
    SimplePublisher() : Node("simple_publisher"), counter_(0)
    {
        // Create publisher
        publisher_ = this->create_publisher<std_msgs::msg::String>("chatter", 10);
        
        // Create timer (500ms)
        timer_ = this->create_wall_timer(
            500ms,
            std::bind(&SimplePublisher::timer_callback, this));
        
        RCLCPP_INFO(this->get_logger(), "Simple Publisher has started!");
    }

private:
    void timer_callback()
    {
        auto message = std_msgs::msg::String();
        message.data = "Hello World: " + std::to_string(counter_);
        
        RCLCPP_INFO(this->get_logger(), "Publishing: '%s'", message.data.c_str());
        publisher_->publish(message);
        
        counter_++;
    }
    
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
    size_t counter_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<SimplePublisher>());
    rclcpp::shutdown();
    return 0;
}
