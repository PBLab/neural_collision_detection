FILE(REMOVE_RECURSE
  "CMakeFiles/docs"
  "../doc/doxygen/index.html"
)

# Per-language clean rules from dependency scanning.
FOREACH(lang)
  INCLUDE(CMakeFiles/docs.dir/cmake_clean_${lang}.cmake OPTIONAL)
ENDFOREACH(lang)
