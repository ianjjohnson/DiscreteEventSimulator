#ifndef CLIENT_C
#define CLIENT_C

#include <stdlib.h>
#include "messagequeue.c"

typedef struct client{

  int id;
  message_queue queue;

} client;

client make_client(int id){

  client c;
  c.id = id;
  c.queue = make_queue();
  return c;

}

void send_message(client* c, message m){

  add_to_queue(&(c->queue), m);

}

void process_messages_for_time(client* clients, int client_id, int time){

  client* c = clients + client_id;

  if(DEBUG == 3) printf("Inbox of client %i has %i messages at time %i\n", client_id, c->queue.num_messages, time);

  while(min_arrival_time(&(c->queue)) == time && c->queue.num_messages > 0){

    message m = top(&(c->queue));
    send_message(clients + m.sender, make_message("Hello!", c->id, time, time+1, 0, 0));

    if(DEBUG) printf("Message: %s received by client %i from client %i at time %i.\n", m.content, c->id, m.sender, time);

  }

}

void delete_clients(client* clients, int num_clients){

  for(int i = 0; i < num_clients; i++)
    delete_queue(clients[i].queue);

}



#endif
