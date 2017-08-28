

#ifndef CONTROLLER_H
#define CONTROLLER_H

#define MAX_COST 100
#define DENSITY 0.4

#include <time.h>
#include <stdlib.h>

typedef struct controller {

  int** adjacencies;
  int num_clients;


} controller;

controller make_controller(int num_clients){

  srand(time(NULL));

  controller c;
  c.num_clients = num_clients;

  c.adjacencies = malloc(num_clients * sizeof(int*));
  for(int i = 0; i < num_clients; i++){

    c.adjacencies[i] = malloc(num_clients * sizeof(int));
    memset(c.adjacencies[i], 0, num_clients * sizeof(int));

  }

  for(int i = 0; i < num_clients; i++){

    int num_edges = 0;

    for(int j = 0; j < num_clients; j++){

      if(i == j){c.adjacencies[i][j] = -1; continue;}

      if(c.adjacencies[i][j]) continue;

      if(((rand() * 1.0) / RAND_MAX) <= DENSITY){

        int cost = (int)(((rand() * 1.0) / RAND_MAX) * MAX_COST);\
        c.adjacencies[i][j] = cost;
        c.adjacencies[j][i] = cost;

      } else {

        c.adjacencies[i][j] = -1;

      }

    }
  }

  return c;

}

void print_adjacencies(controller* c){

  int space = 3;

  printf("Adjacency Matrix:");
  for(int i = 0; i < c->num_clients; i++){
    printf("\n[");
    for(int j = 0; j < c->num_clients; j++){
      printf("%*d,", space, c->adjacencies[i][j]);
    }
    printf("\b]");
  }
  printf("\n");

}


void delete_controller(controller c){

  for(int i = 0; i < c.num_clients; i++)
    free(c.adjacencies[i]);

  free(c.adjacencies);

}

#endif
