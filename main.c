
#include <stdio.h>
#include "client.c"


int main(int argc, char* argv[]){

  if(argc != 2){
    printf("Usage: ./simulator [num_clients]");
    return 1;
  }

  int num_clients = atoi(argv[1]);



  return 0;

}
