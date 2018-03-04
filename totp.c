#include <stdio.h>
#include <strings.h>

#include <openssl/sha.h>

#define sha_block_size 64
#define OPAD "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
#define IPAD "mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm"

int max(int a, int b){
    if(a > b) {
        return a;
    } else {
        return b;
    }
}

void str_xor(char** c, char* a, char* b) {
    
    int lenA = strlen(a);
    int lenB = strlen(b);
    
    int lenC = max(lenA, lenB);
    *c = malloc(lenC);    

    char* aaux = malloc(lenC);
    char* baux = malloc(lenC);
        
    int i;
    for(i = lenC; i >= 0; i--){
        int itAux = lenC - i;
        if(lenA < i){
            aaux[itAux] = '\x00';
        } else {
            aaux[itAux] = a[itAux];
        }

        if(lenB < i){
            baux[itAux] = '\x00';
        } else {
            baux[itAux] = b[itAux];
        }
    }

    for(i = 0; i < lenC; i++){
        *(*c + i) = aaux[i] ^ baux[i];
    }
}


void sha1(char** output, char* input){
    int lenI = strlen(input);

    SHA1(input, lenI, output); 
}

void hmac(char** res, char* K, char* m){
    
}

void main(){
    char* a = "abc";
    char* b= "def";
    char* c;

    str_xor(&c, a, b);

    printf("%s\n", c);
    
    str_xor(&a, c, b);
   
    printf("%s\n", a);

    sha1(&c, a);
    
    printf("%02x\n", c);

}
