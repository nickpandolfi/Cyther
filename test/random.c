
#include <stdlib.h>

#include "random.h"

/** Helper functions to aid with the random generation of data
 * @author Nicholas C. Pandolfi
 */


/** The function will produce a single printable character (ascii range 33 to 126)
 * @return A single randomized character
 */

char random_character(){
  char c;
  int i;
  
  // Generate a random lowercase character (ASCII range 97 - 122 inclusive)
  i = random_number(97, 123);

  // Get the character that the int i represents
  c = (char)i;
  
  return c;
}


/** This function will generate a string of random printable characters in the range of 33 - 126
 * @param length The length of the string you want to return. Filled entirely with random characters.
 * @return The pointer to the null terminated string
 */

char *random_string(size_t length){
  char *string;
  char c;

  // The memoy to allocate for the string
  string = (char *)malloc(length + 1);
  
  int i;
  // Create the string, character by character
  for (i = 0; i < length; i++){
    c = random_character();
    string[i] = c;
  }

  // Tack on the null terminator to finish construction of the string
  string[length] = '\0';

  return string;
}


/** Generates a random number (int)
 * @param start The starting number to generate from (inclusive)
 * @param end The maximum number to generate to (exclusive)
 * @return The randomly generated numer (int)
 */

int random_number(int start, int end){
  int random_num;
  
  // Generates the random number "[start, end)"
  random_num = (rand() % ((end - start))) + start;
  
  return random_num;

}
