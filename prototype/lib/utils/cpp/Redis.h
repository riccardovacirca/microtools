#pragma once

#include <string>
#include <vector>

namespace mt {

/**
 * @brief Redis client wrapper for hiredis library
 */
class Redis {
public:
  /**
   * @brief Constructor
   * @param host Redis server host
   * @param port Redis server port
   */
  Redis(const std::string &host, int port);

  /**
   * @brief Destructor
   */
  ~Redis();

  /**
   * @brief Connect to Redis server
   */
  void connect();

  /**
   * @brief Disconnect from Redis server
   */
  void disconnect();

  /**
   * @brief List all keys matching pattern
   * @param pattern Key pattern (default "*" for all keys)
   * @return Vector of matching keys
   */
  std::vector<std::string> keys(const std::string &pattern);

  /**
   * @brief Get value for key
   * @param key Key name
   * @return Value as string (empty if key not found)
   */
  std::string get(const std::string &key);

  /**
   * @brief Set key to value
   * @param key Key name
   * @param value Value to set
   */
  void set(const std::string &key, const std::string &value);

  /**
   * @brief Delete key
   * @param key Key name
   */
  void del(const std::string &key);

private:
  std::string host_;
  int port_;
  void *context_;
};

}  // namespace mt
