#include "ftdi.h"
#include "stdio.h"
int main()
{
  printf ("%d\n", sizeof(struct ftdi_context));
}
