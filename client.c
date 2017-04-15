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


#endif
