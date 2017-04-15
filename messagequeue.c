#ifndef MSGQ_C
#define MSGQ_C

#include <stdlib.h>
#include <string.h>

typedef struct message {

  char* content;
  int sender;

  int send_time;
  int arrive_time;

} message;

typedef struct message_queue{

  message* messages;
  int num_messages;
  int capacity;

} message_queue;

message make_message(char* c, int s, int st, int at){

  message m;
  m.content = c;
  m.sender = s;
  m.send_time = st;
  m.arrive_time = at;
  return m;

}

message_queue make_queue(){

  message_queue q;
  q.num_messages = 0;
  q.capacity = 10;
  q.messages = malloc(10 * sizeof(message));

  return q;

}

void resize(message_queue* q){

  message* new_msgs = malloc(2 * q->capacity * sizeof(message));
  memcpy(new_msgs, q->messages, q->capacity * sizeof(message));
  free(q->messages);
  q->messages = new_msgs;
  q->capacity *= 2;

}

void swap(message* msgs, int a, int b){

  message tmp = msgs[a];
  msgs[a] = msgs[b];
  msgs[b] = tmp;

}

void heapify(message_queue* q){

  int index = q->num_messages - 1;
  int next = (index-1) / 2;

  while(next >= 0){

    if(q->messages[index].arrive_time < q->messages[next].arrive_time){
        swap(q->messages, index, next);
        index = next;
        next = (index - 1) / 2;
    } else break;

  }

}

void add_to_queue(message_queue* q, message m){

  if(q->num_messages == q->capacity) resize(q);
  q->messages[q->num_messages] = m;
  q->num_messages++;
  heapify(q);

}

int min_arrival_time(message_queue* q){
  return (q->num_messages == 0)? -1 : q->messages[0].arrive_time;
}

message top(message_queue* q){

  message t = q->messages[0];
  q->messages[0] = q->messages[q->num_messages - 1];
  q->num_messages--;
  swap(q->messages, 0, q->num_messages);
  heapify(q);
  return t;

}

void delete(message_queue* q){

  free(q->messages);

}


#endif
