#pragma once

#include "Data.h"
#include <memory>

namespace nanodbc {
class connection;
class result;
} // namespace nanodbc

namespace mt {

/**
 * @brief Database connection and query handler with ODBC support
 */
class DB {
public:
  /**
   * @brief Constructor
   */
  DB();
  /**
   * @brief Destructor
   */
  ~DB();
  /**
   * @brief Connects to database using ODBC connection string
   * @param connection_string ODBC connection string (DSN or full connection string)
   */
  void connect(const std::string &connection_string);
  /**
   * @brief Disconnects from database
   */
  void disconnect();
  /**
   * @brief Checks if connected to database
   * @return true if connected, false otherwise
   */
  bool is_connected() const;
  /**
   * @brief Executes a SQL query that modifies data
   * @param sql SQL query to execute (INSERT, UPDATE, DELETE)
   * @return Number of affected rows
   */
  int query(const std::string &sql);
  /**
   * @brief Executes a SELECT query and returns first row
   * @param sql SQL SELECT query
   * @return First record as Record (map of field name to Field value)
   */
  Record select(const std::string &sql);
  /**
   * @brief Executes a SELECT query and returns all rows
   * @param sql SQL SELECT query
   * @return All records as Recordset (vector of Record)
   */
  Recordset select_all(const std::string &sql);
  /**
   * @brief Opens a cursor for iterating through query results
   * @param sql SQL SELECT query
   */
  void cursor_open(const std::string &sql);
  /**
   * @brief Checks if cursor has more rows available
   * @return true if more rows available, false otherwise
   */
  bool cursor_has_next();
  /**
   * @brief Retrieves next row from cursor
   * @return Next record as Record
   */
  Record cursor_next();
  /**
   * @brief Closes the cursor and releases resources
   */
  void cursor_close();

private:
  std::unique_ptr<nanodbc::connection> connection_;
  std::unique_ptr<nanodbc::result> cursor_;
  bool cursor_first_call_;
  bool cursor_has_data_;
};

} // namespace mt
