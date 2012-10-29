#include <stdio.h>
#include "mylib.h"
#include "config.h"

int main( int argc, char* argv[] )
{
  int result = my_func(1,2);
  printf("tmpl_app %i\n",result);
  return 0;
}
