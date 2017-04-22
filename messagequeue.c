#ifndef MSGQ_C
#define MSGQ_C

#define MIN(X, Y) (((X) < (Y))? (X) : Y);

#include <stdlib.h>
#include <string.h>
#include <limits.h>

typedef struct message {

  char* content;

  int flow_id;
  int packet_number;

  int sender;

  int send_time;
  int arrive_time;

} message;

typedef struct message_queue{

  message* messages;
  int num_messages;
  int capacity;

} message_queue;

message make_message(char* content, int s, int st, int at, int f_id, int p_no){

  message m;
  m.content = content;
  m.flow_id = f_id;
  m.packet_number = p_no;
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

void heapify_top(message_queue* q){

  int index = 0;

  while(index < q->num_messages){

    int left  = index * 2 + 1;
    int right = index * 2 + 2;

    int left_val  = (left >= q->num_messages)?  INT_MAX : q->messages[left].arrive_time;
    int right_val = (right >= q->num_messages)? INT_MAX : q->messages[right].arrive_time;

    int loc_min = ((left_val < right_val)? left : right);
    int min = MIN(left_val, right_val);

    if(min < q->messages[index].arrive_time) swap(q->messages, index, loc_min);

    index = loc_min;

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
  heapify_top(q);
  return t;

}

void delete(message_queue* q){

  free(q->messages);

}


#endif
