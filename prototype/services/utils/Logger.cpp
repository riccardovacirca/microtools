#include "Logger.h"

#include <filesystem>
#include <spdlog/sinks/basic_file_sink.h>
#include <spdlog/spdlog.h>

namespace mt {

Logger::Logger(const std::string &name, const std::string &log_file_path) {
  std::filesystem::path file_path(log_file_path);
  std::filesystem::path dir_path = file_path.parent_path();
  if (!dir_path.empty() && !std::filesystem::exists(dir_path)) {
    std::filesystem::create_directories(dir_path);
  }
  logger_ = spdlog::basic_logger_mt(name, log_file_path);
  logger_->set_pattern("[%Y-%m-%d %H:%M:%S.%e] [%l] %v");
  logger_->set_level(spdlog::level::info);
}

Logger::~Logger() {
  if (logger_) {
    logger_->flush();
  }
}

void Logger::info(const std::string &message) {
  if (logger_) {
    logger_->info(message);
  }
}

void Logger::warn(const std::string &message) {
  if (logger_) {
    logger_->warn(message);
  }
}

void Logger::error(const std::string &message) {
  if (logger_) {
    logger_->error(message);
  }
}

void Logger::debug(const std::string &message) {
  if (logger_) {
    logger_->debug(message);
  }
}

} // namespace mt
