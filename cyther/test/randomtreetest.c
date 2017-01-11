#include <stdio.h>
#include <time.h>
#include <stdlib.h>

#include "tree.h"
#include "random.h"

// The maximum/minimum length of the randomly generated strings
#define MAX_LENGTH (20)
#define MIN_LENGTH (10)

// The amount of nodes to construct
#define NODES (50)


/** This main program will generate random strings of random length and feed them into a tree
 * one by one. It will then print the tree, which is already sorted. The traversal is done
 * 'inorder'. The tree is then freed.
 * @author Nicholas C. Pandolfi
 */

int main(){
  // Initialize the random generator
  srand(time(NULL));
  
  int length;
  char *value;
  
  // Initialize the first node (root of the tree)
  length = random_number(0, MAX_LENGTH);
  value = random_string(length);
  Tnode *tree = add_tnode(NULL, value);

  // Run the loop to add more nodes
  int i;
  for (i = 0; i < NODES; i++){
    // Calculate the length of the random string (random)
    length = random_number(MIN_LENGTH, MAX_LENGTH);
    
    // Get the random string of 'length' length
    value = random_string(length);
    
    // Generate a new node with that new randomized string
    add_tnode(tree, value);
  }

  // Print the full tree generated
  printf("\n");
  print_tree_inorder(tree);
  printf("\n");

  // Free the tree and all the nodes in it ('1' means to also free the values inside of the nodes)
  free_tree(tree, 1);
}
