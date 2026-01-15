#include "Env.h"

#include <cstdlib>
#include <stdexcept>

extern char **environ;

namespace mt {

Env::Env() {}

Record Env::all() const {
  Record result;
  if (environ == nullptr) {
    return result;
  }
  char **env = environ;
  while (*env != nullptr) {
    std::string line(*env);
    size_t pos = line.find('=');
    if (pos != std::string::npos) {
      std::string key = line.substr(0, pos);
      std::string value = line.substr(pos + 1);
      result[key] = value;
    }
    env++;
  }
  return result;
}

Field Env::get(const std::string &key) const {
  const char *value = std::getenv(key.c_str());
  if (value == nullptr) {
    throw std::runtime_error("Environment variable not found: " + key);
  }
  return std::string(value);
}

bool Env::has(const std::string &key) const {
  const char *value = std::getenv(key.c_str());
  return value != nullptr;
}

} // namespace mt
