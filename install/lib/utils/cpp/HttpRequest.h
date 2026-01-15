#pragma once

#include "Data.h"
#include <memory>
#include <vector>

namespace httplib {
class Request;
}

namespace mt {

/**
 * @brief HTTP request wrapper for httplib::Request
 */
class HttpRequest {
public:
  /**
   * @brief Constructor
   * @param native_request Pointer to httplib::Request object
   */
  HttpRequest(void *native_request);
  /**
   * @brief Destructor
   */
  ~HttpRequest();
  /**
   * @brief Gets path segments from URI
   * @return Vector of path segments (e.g., "/api/users" -> ["api", "users"])
   */
  std::vector<std::string> get_path() const;
  /**
   * @brief Gets full URI including query string
   * @return Full URI (e.g., "/api/users?id=1")
   */
  std::string get_uri() const;
  /**
   * @brief Gets HTTP protocol version
   * @return Protocol version (e.g., "HTTP/1.1")
   */
  std::string get_protocol() const;
  /**
   * @brief Gets HTTP method
   * @return HTTP method (e.g., "GET", "POST")
   */
  std::string get_method() const;
  /**
   * @brief Gets all request headers
   * @return Record containing all headers as key-value pairs
   */
  Record get_headers() const;
  /**
   * @brief Gets specific header value
   * @param key Header name
   * @return Header value (empty string if not found)
   */
  std::string get_header(const std::string &key) const;
  /**
   * @brief Gets all cookies
   * @return Record containing all cookies as key-value pairs
   */
  Record get_cookies() const;
  /**
   * @brief Gets specific cookie value
   * @param key Cookie name
   * @return Cookie value (empty string if not found)
   */
  std::string get_cookie(const std::string &key) const;
  /**
   * @brief Gets query string
   * @return Query string without leading "?" (e.g., "id=1&name=test")
   */
  std::string get_query() const;
  /**
   * @brief Gets URL parameters
   * @return Record containing URL parameters as key-value pairs
   */
  Record get_params() const;
  /**
   * @brief Gets uploaded files information
   * @return Recordset containing file metadata (name, filename, content_type, size)
   */
  Recordset get_uploaded_files() const;
  /**
   * @brief Gets multipart form fields
   * @return Record containing form field values
   */
  Record get_multipart_fields() const;

private:
  void *request_;
};

} // namespace mt
