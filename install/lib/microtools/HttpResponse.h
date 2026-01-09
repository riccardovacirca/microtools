#pragma once

#include "Data.h"
#include <string>

namespace mt {

/**
 * @brief HTTP response builder
 */
class HttpResponse {
public:
  /**
   * @brief Constructor
   */
  HttpResponse();
  /**
   * @brief Destructor
   */
  ~HttpResponse();
  /**
   * @brief Sets HTTP status code
   * @param status HTTP status code (e.g., 200, 404, 500)
   */
  void set_status(int status);
  /**
   * @brief Gets current HTTP status code
   * @return HTTP status code
   */
  int get_status() const;
  /**
   * @brief Sets response header
   * @param key Header name
   * @param value Header value
   */
  void set_header(const std::string &key, const std::string &value);
  /**
   * @brief Sets Content-Type header
   * @param value Content type (e.g., "application/json", "text/html")
   */
  void set_content_type(const std::string &value);
  /**
   * @brief Sets response body from Record
   * @param body Response body as Record
   */
  void set_body(const Record &body);
  /**
   * @brief Gets response body
   * @return Response body as Record
   */
  Record get_body() const;
  /**
   * @brief Gets all response headers
   * @return Record containing all headers
   */
  Record get_headers() const;
  /**
   * @brief Sets a cookie
   * @param key Cookie name
   * @param value Cookie value
   * @param path Cookie path (default: "/")
   * @param max_age Cookie max age in seconds (0 = session cookie)
   */
  void set_cookie(const std::string &key, const std::string &value, const std::string &path, int max_age);
  /**
   * @brief Marks response as file download
   */
  void set_download();

private:
  int status_;
  Record headers_;
  Record body_;
};

} // namespace mt
