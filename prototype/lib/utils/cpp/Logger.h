#pragma once

#include <memory>
#include <string>

namespace spdlog {
class logger;
}

namespace mt {

/**
 * @brief Logging handler with multiple severity levels (stateful)
 */
class Logger {
public:
  /**
   * @brief Constructor
   * @param name Logger name
   * @param log_file_path Path to log file
   */
  Logger(const std::string &name, const std::string &log_file_path);
  /**
   * @brief Destructor
   */
  ~Logger();
  /**
   * @brief Logs an informational message
   * @param message Message to log
   */
  void info(const std::string &message);
  /**
   * @brief Logs a warning message
   * @param message Message to log
   */
  void warn(const std::string &message);
  /**
   * @brief Logs an error message
   * @param message Message to log
   */
  void error(const std::string &message);
  /**
   * @brief Logs a debug message
   * @param message Message to log
   */
  void debug(const std::string &message);

private:
  std::shared_ptr<spdlog::logger> logger_;
};

} // namespace mt
