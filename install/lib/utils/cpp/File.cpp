#include "File.h"

#include <sstream>
#include <stdexcept>

namespace mt {

File::File(const std::string &path) {
  path_ = path;
  stream_ = std::make_unique<std::fstream>();
  is_open_ = false;
}

File::~File() {
  if (is_open_) {
    close();
  }
}

void File::open() {
  if (is_open_) {
    throw std::runtime_error("File already open: " + path_);
  }
  stream_->open(path_.c_str(), std::ios::in | std::ios::out | std::ios::app);
  if (!stream_->is_open()) {
    throw std::runtime_error("Cannot open file: " + path_);
  }
  is_open_ = true;
}

void File::close() {
  if (!is_open_) {
    return;
  }
  if (stream_->is_open()) {
    stream_->close();
  }
  is_open_ = false;
}

bool File::is_open() const { return is_open_; }

std::string File::read() {
  if (!is_open_) {
    throw std::runtime_error("File not open: " + path_);
  }
  stream_->seekg(0, std::ios::beg);
  std::ostringstream buffer;
  buffer << stream_->rdbuf();
  return buffer.str();
}

void File::write(const std::string &content) {
  if (!is_open_) {
    throw std::runtime_error("File not open: " + path_);
  }
  stream_->seekp(0, std::ios::beg);
  stream_->clear();
  *stream_ << content;
  stream_->flush();
}

void File::append(const std::string &content) {
  if (!is_open_) {
    throw std::runtime_error("File not open: " + path_);
  }
  stream_->seekp(0, std::ios::end);
  *stream_ << content;
  stream_->flush();
}

} // namespace mt
