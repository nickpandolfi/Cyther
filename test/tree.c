#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include "tree.h"


/** Definitions for the creation and modification of a linked tree data structure
 * @author Nicholas C. Pandolfi
 */


/** This function adds a node to an already existing tree, or creates the first node to a new tree
 * @param current_tnode A pointer to the node to create off of. NULL can be used to denote a new tree
 * @param value The pointer to the string that the node will hold
 * @return The pointer to the Tnode created
 */

Tnode *add_tnode(Tnode *current_tnode, char *value){
  if (!current_tnode){
    // Allocate a new node
    Tnode *new_node = (Tnode *) malloc(sizeof(Tnode));

    // Put the value into the new node, and initialize the pointers of both children to NULL
    new_node->value = value;
    new_node->left_child = NULL;
    new_node->right_child = NULL;

    // Return a pointer to that new node
    return new_node;

  } else {
    // Compare the value given vs the value of current_tnode
    int cmp;
    cmp = strcmp(current_tnode->value, value);
    
    // Branch according to the value (negative to left, positive to right)
    Tnode *return_value;
    if (cmp <= 0){
      return_value = add_tnode(current_tnode->left_child, value);
      if (return_value){
        current_tnode->left_child = return_value;
      } else return NULL;
    } else {
      return_value = add_tnode(current_tnode->right_child, value);
      if (return_value){
        current_tnode->right_child = return_value;
      } else return NULL;
    }
  }
}


/** Print the tree given in order, treating the node passed in as the root node
 * @param current_tnode The root node to print
 */

void print_tree_inorder(Tnode *current_tnode){
  
  // Visit the left child
  if (current_tnode->left_child){
    print_tree_inorder(current_tnode->left_child);
  }
  
  // Print the value in the current node
  printf("%s\n", current_tnode->value);
  
  // Visit the right child
  if (current_tnode->right_child){
    print_tree_inorder(current_tnode->right_child);
  }
}


/** Frees all nodes in the tree, but not the 'value' parameter in each node
 * @param current_tnode The node to tret as the root of a tree to be freed
 * @param free_value An int hat acts like a boolean to denote if user wants to ALSO free
 * value field in each node
 */

void free_tree(Tnode *current_tnode, int free_value){
  // Free the left child
  if (current_tnode->left_child){
    free_tree(current_tnode->left_child, free_value);
  }

  // Free the right child
  if (current_tnode->right_child){
    free_tree(current_tnode->right_child, free_value);
  }

  // Free the current node
  if (free_value){
    free(current_tnode->value);
  }
  free(current_tnode);
}

