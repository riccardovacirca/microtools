#pragma once

#include "Data.h"

namespace mt {

/**
 * @brief Environment variables handler
 */
class Env {
public:
  /**
   * @brief Constructor
   */
  Env();
  /**
   * @brief Gets all environment variables
   * @return Record containing all environment variables as key-value pairs
   */
  Record all() const;
  /**
   * @brief Gets value of a specific environment variable
   * @param key Environment variable name
   * @return Field containing the value (empty string if not found)
   */
  Field get(const std::string &key) const;
  /**
   * @brief Checks if an environment variable exists
   * @param key Environment variable name
   * @return true if variable exists, false otherwise
   */
  bool has(const std::string &key) const;
};

}  // namespace mt
