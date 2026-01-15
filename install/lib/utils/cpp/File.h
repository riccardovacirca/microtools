#pragma once

#include <fstream>
#include <memory>
#include <string>

namespace mt {

/**
 * @brief File I/O handler with RAII and explicit open/close
 */
class File {
public:
  /**
   * @brief Constructor
   * @param path File path
   */
  File(const std::string &path);
  /**
   * @brief Destructor (closes file if open)
   */
  ~File();
  /**
   * @brief Opens the file for reading and writing
   */
  void open();
  /**
   * @brief Closes the file
   */
  void close();
  /**
   * @brief Checks if file is currently open
   * @return true if file is open, false otherwise
   */
  bool is_open() const;
  /**
   * @brief Reads entire file content
   * @return File content as string
   */
  std::string read();
  /**
   * @brief Writes content to file (overwrites existing content)
   * @param content Content to write
   */
  void write(const std::string &content);
  /**
   * @brief Appends content to file
   * @param content Content to append
   */
  void append(const std::string &content);

private:
  std::string path_;
  std::unique_ptr<std::fstream> stream_;
  bool is_open_;
};

} // namespace mt
