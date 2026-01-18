#include "HttpResponse.h"

namespace mt {

HttpResponse::HttpResponse() {
  status_ = 200;
  body_["err"] = std::string("");
  body_["log"] = std::string("");
  body_["out"] = std::string("");
}

HttpResponse::~HttpResponse() {}

void HttpResponse::set_status(int status) {
  status_ = status;
}

int HttpResponse::get_status() const {
  return status_;
}

void HttpResponse::set_header(const std::string &key, const std::string &value) {
  headers_[key] = value;
}

void HttpResponse::set_content_type(const std::string &value) {
  set_header("Content-Type", value);
}

void HttpResponse::set_body(const Record &body) {
  body_ = body;
}

Record HttpResponse::get_body() const {
  return body_;
}

Record HttpResponse::get_headers() const {
  return headers_;
}

void HttpResponse::set_cookie(const std::string &key, const std::string &value, const std::string &path, int max_age) {
  std::string cookie = key + "=" + value + "; Path=" + path;
  if (max_age > 0) {
    cookie += "; Max-Age=" + std::to_string(max_age);
  }
  set_header("Set-Cookie", cookie);
}

void HttpResponse::set_download() {
  set_header("Content-Disposition", "attachment");
}

} // namespace mt
