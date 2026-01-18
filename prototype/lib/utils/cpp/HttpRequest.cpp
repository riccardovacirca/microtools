#include "HttpRequest.h"
#include <httplib.h>
#include <stdexcept>

namespace mt {

HttpRequest::HttpRequest(void *native_request) {
  request_ = native_request;
}

HttpRequest::~HttpRequest() {
}

std::vector<std::string> HttpRequest::get_path() const {
  httplib::Request *req = static_cast<httplib::Request*>(request_);
  std::vector<std::string> segments;
  std::string path = req->path;
  if (path.empty() || path[0] != '/') {
    return segments;
  }
  size_t start = 1;
  size_t end = path.find('/', start);
  while (end != std::string::npos) {
    if (end > start) {
      segments.push_back(path.substr(start, end - start));
    }
    start = end + 1;
    end = path.find('/', start);
  }
  if (start < path.length()) {
    segments.push_back(path.substr(start));
  }
  return segments;
}

std::string HttpRequest::get_uri() const {
  httplib::Request *req = static_cast<httplib::Request*>(request_);
  return req->path;
}

std::string HttpRequest::get_protocol() const {
  httplib::Request *req = static_cast<httplib::Request*>(request_);
  return req->version;
}

std::string HttpRequest::get_method() const {
  httplib::Request *req = static_cast<httplib::Request*>(request_);
  return req->method;
}

Record HttpRequest::get_headers() const {
  httplib::Request *req = static_cast<httplib::Request*>(request_);
  Record result;
  for (const auto &[key, value] : req->headers) {
    result[key] = value;
  }
  return result;
}

std::string HttpRequest::get_header(const std::string &key) const {
  httplib::Request *req = static_cast<httplib::Request*>(request_);
  if (req->has_header(key.c_str())) {
    return req->get_header_value(key.c_str());
  }
  return "";
}

Record HttpRequest::get_cookies() const {
  httplib::Request *req = static_cast<httplib::Request*>(request_);
  Record cookies;
  std::string cookie_header = get_header("Cookie");
  return cookies;
}

std::string HttpRequest::get_cookie(const std::string &key) const {
  Record cookies = get_cookies();
  auto it = cookies.find(key);
  if (it != cookies.end()) {
    if (std::holds_alternative<std::string>(it->second)) {
      return std::get<std::string>(it->second);
    }
  }
  return "";
}

std::string HttpRequest::get_query() const {
  httplib::Request *req = static_cast<httplib::Request*>(request_);
  size_t pos = req->path.find('?');
  if (pos != std::string::npos) {
    return req->path.substr(pos + 1);
  }
  return "";
}

Record HttpRequest::get_params() const {
  httplib::Request *req = static_cast<httplib::Request*>(request_);
  Record result;
  for (const auto &[key, value] : req->params) {
    result[key] = value;
  }
  return result;
}

Recordset HttpRequest::get_uploaded_files() const {
  httplib::Request *req = static_cast<httplib::Request*>(request_);
  Recordset result;
  for (const auto &[key, file] : req->form.files) {
    Record file_info;
    file_info["name"] = file.name;
    file_info["filename"] = file.filename;
    file_info["content_type"] = file.content_type;
    file_info["size"] = static_cast<long>(file.content.size());
    result.push_back(file_info);
  }
  return result;
}

Record HttpRequest::get_multipart_fields() const {
  httplib::Request *req = static_cast<httplib::Request*>(request_);
  Record result;
  for (const auto &[key, field] : req->form.fields) {
    result[key] = field.content;
  }
  return result;
}

}  // namespace mt
