
/** Just some function prototypes for the tree.c source code
 * @author Nicholas C. Pandolfi
 */


/** Struct to define a tree. Holds a c style string pointer and pointers to left and right children.
 */

struct tnode {
  char *value;
  struct tnode *left_child;
  struct tnode *right_child;
};

typedef struct tnode Tnode;



// Function prototypes

Tnode *add_tnode(Tnode *current_tnode, char *value);
void print_tree_inorder(Tnode *current_tnode);
void free_tree(Tnode *current_tnode, int free_value);
