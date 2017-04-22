#define RUNTIME 5
#define DEBUG 0

#include <stdio.h>
#include "client.c"
#include "controller.c"

void startup(client* clients, int num_clients){

  for(int i = 0; i < num_clients; i++) clients[i] = make_client(i);

  for(int i = 0; i < num_clients; i++)
    for(int j = i+1; j < num_clients; j++)
      send_message(clients + j, make_message("Init_message", i, -1, 0, 0, 0));

}

void loop(client* clients, int num_clients, int time){

  for(int i = 0; i < num_clients; i++)
    process_messages_for_time(clients, i, time);

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
    loop(clients, num_clients, i);

  free(clients);

  return 0;

}
