CPP_CLASS_STYLE microtools_cpp_explicit

# LANGUAGE PROFILE

BASE STANDARD: C++98

ALLOWED MODERN FEATURES:
  - std::unique_ptr (C++11) - MANDATORY for heap allocation
  - std::variant (C++17) - Type-safe union for heterogeneous values
  - #pragma once - Preferred over traditional header guards
  - auto keyword - AVOID, always use explicit types

# SYNTAX RULES

EXPLICITNESS:
  - Principle: Totally explicit syntax - no implicit constructs
  - Constructor initialization: explicit body assignment
  - Type declaration: always explicit, never auto

FORBIDDEN:
  ✗ Constructor() : member_(value) {}  // implicit initialization
  ✗ auto value = getValue();           // implicit type

REQUIRED:
  ✓ Constructor() {                    // explicit assignment
      member_ = value;
    }
  ✓ std::string value = getValue();    // explicit type

# FORMATTING

INDENTATION:
  - 2 spaces (no tabs, no 4 spaces)
  - Example:
    ```cpp
    void method() {
      if (condition) {
        doSomething();
      }
    }
    ```

BLANK LINES:
  - NO blank lines inside function bodies (compact style)
  - Forbidden:
    ```cpp
    void method() {
      int x = 5;
                    // ✗ no blank line here
      return x * 2;
    }
    ```
  - Required:
    ```cpp
    void method() {
      int x = 5;
      return x * 2;  // ✓ compact
    }
    ```

EMPTY FUNCTIONS:
  - Single line: Constructor() {}

SIMPLE METHODS:
  - Single line when trivial: void clear() { buffer_->clear(); }

BRACES:
  - Egyptian style (opening brace on same line)
  - Example: if (condition) {

REFERENCE SYMBOL:
  - LLVM style: symbol & next to variable, not type
  - Required: const std::string &name
  - Forbidden: const std::string& name

# DOCUMENTATION

HEADER FILES (.h):
  - MANDATORY Doxygen comments for all public methods
  - Style: Javadoc (/** ... */)
  - Required tags: @brief, @param (if params), @return (if not void)

EXAMPLE:
```cpp
/**
 * @brief Connects to database
 * @param connection_string DSN connection string
 */
void connect(const std::string &connection_string);
```

IMPLEMENTATION FILES (.cpp):
  - NO comments in .cpp files
  - Only code, documentation is in .h
  - Rationale: self-documenting code

# NAMING CONVENTIONS

CLASSES:
  - PascalCase: DB, File, Logger

METHODS:
  - snake_case: connect(), cursor_open()

PRIVATE MEMBERS:
  - snake_case with trailing underscore: connection_, cursor_

NAMESPACES:
  - lowercase, short: mt

# MEMORY MANAGEMENT

MANDATORY UNIQUE_PTR:
  - ALWAYS use std::unique_ptr for heap allocation
  - Forbidden: Type* ptr = new Type();
  - Required: std::unique_ptr<Type> ptr = std::make_unique<Type>();

NO MANUAL DELETE:
  - Never use explicit delete
  - unique_ptr handles everything automatically

EXPLICIT ASSIGNMENT:
  - In constructor body: ptr_ = std::make_unique<T>();

# PARAMETER PASSING

DEFAULT RULE:
  - const reference for objects: const Type &param

OUTPUT PARAMETERS:
  - reference: Type &output_param

PRIMITIVES:
  - by value: int, bool, char

FORBIDDEN:
  - by value for std::string, containers, objects

# DESIGN PRINCIPLES

SIMPLICITY FIRST:
  - Use typedef when base class has all needed methods
  - Use wrapper class only for custom logic or RAII

EXAMPLE:
```cpp
// Simple typedef when enough
typedef std::vector<Record> Recordset;

// Wrapper only when adding behavior
class DB {
  // custom logic here
};
```

# COMPLETE EXAMPLE

HEADER FILE (File.h):
```cpp
#pragma once

#include <string>

namespace mt {

/**
 * @brief File I/O handler
 */
class File {
public:
  /**
   * @brief Constructor
   * @param path File path
   */
  File(const std::string &path);

  /**
   * @brief Opens the file
   */
  void open();

  /**
   * @brief Reads entire file content
   * @return File content as string
   */
  std::string read();

private:
  std::string path_;
};

}  // namespace mt
```

IMPLEMENTATION FILE (File.cpp):
```cpp
#include "File.h"
#include <fstream>

namespace mt {

File::File(const std::string &path) {
  path_ = path;
}

void File::open() {
  stream_ = std::make_unique<std::fstream>();
  stream_->open(path_.c_str());
  if (!stream_->is_open()) {
    throw std::runtime_error("Cannot open: " + path_);
  }
}

std::string File::read() {
  std::ostringstream buffer;
  buffer << stream_->rdbuf();
  return buffer.str();
}

}  // namespace mt
```

# ANTI-PATTERNS (FORBIDDEN)

- initialization_list: Class() : ptr_(value) {}
- auto_keyword: auto value = func();
- raw_pointers_ownership: Type* owned_;
- pass_by_value_objects: void func(std::string s)
- blank_lines_in_functions: gaps inside function body
- undocumented_public_methods: missing Doxygen in .h
- wrong_reference_placement: const Type& arg (should be Type &arg)

# REQUIRED PATTERNS

- explicit_body_assignment in constructors
- explicit_types (never auto)
- unique_ptr for heap allocation
- const_reference for object parameters
- doxygen_comments for public methods in .h
- compact_function_bodies (no blank lines)
- LLVM_reference_style (& next to variable)
