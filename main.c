#define RUNTIME 1000000000 //1 million

#include <stdio.h>
#include "client.c"

void startup(client* clients, int num_clients){

  for(int i = 0; i < num_clients; i++) clients[i] = make_client(i);

  for(int i = 0; i < num_clients; i++)
    for(int j = i+1; j < num_clients; j++)
      send_message(clients + j, make_message("Hello!", i, -1, 0));

}

void loop(client* clients, int time){

  return;

}

int main(int argc, char* argv[]){

  if(argc != 2){
    printf("Usage: ./simulator [num_clients]\n");
    return 1;
  }

  int num_clients = atoi(argv[1]);

  client* clients = malloc(num_clients * sizeof(client));

  startup(clients, num_clients);

  for(int i = 0; i < RUNTIME; i++)
    loop(clients, i);

  free(clients);

  return 0;

}
