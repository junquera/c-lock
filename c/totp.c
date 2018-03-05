#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include <openssl/sha.h>

// Sleep
#include <unistd.h>
#include <time.h>

#define sha_block_size SHA_CBLOCK

#define OPAD "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
#define IPAD "mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm"

int max(int a, int b){
    if(a > b) {
        return a;
    } else {
        return b;
    }
}

void str_xor(char* c, int lenA, char* a, int lenB, char* b) {

    //printf("A: %s; B: %s; Len A: %d; Len B: %d;\n", a, b, lenA, lenB);
    int lenC = max(lenA, lenB);

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

    for(i = 0; i < lenC; i++)
        *(c + i) = aaux[i] ^ baux[i];

    free(aaux);
    free(baux);
}

void hmac(char* res, int klen, char* K, int mlen, char* m){

    char* k = malloc(SHA_DIGEST_LENGTH);

    if(klen > sha_block_size){
        SHA1((const unsigned char*) K, klen, (unsigned char*) k);
        klen = SHA_DIGEST_LENGTH;
    } else {
      strcpy(k, K);
    }

    if(klen < sha_block_size) {
        char aux[sha_block_size];

        int s = klen;
        int i;
        for(i = 0; i < sha_block_size; i++) {
            if (sha_block_size - i > s) {
                aux[i] = '\x00';
            } else {
                aux[i] = k[i - sha_block_size + s];
            }
        }

        k = aux;

    }

    char hash[SHA_DIGEST_LENGTH];
    char *o_key_pad = malloc(sha_block_size);
    char *i_key_pad = malloc(sha_block_size);

    str_xor(o_key_pad, sha_block_size, k, sha_block_size, OPAD);
    str_xor(i_key_pad, sha_block_size, k, sha_block_size, IPAD);

    SHA_CTX ctx;

    // Generating SHA1(i_key_pad||m)
    SHA1_Init(&ctx);

    SHA1_Update(&ctx, i_key_pad, sha_block_size);
    SHA1_Update(&ctx, m, mlen);

    SHA1_Final((unsigned char*) hash, &ctx);

    // Generating SHA1(o_key_pad||SHA1(i_key_pad||m))
    SHA1_Init(&ctx);

    SHA1_Update(&ctx, o_key_pad, sha_block_size);
    SHA1_Update(&ctx, (unsigned char*) hash, SHA_DIGEST_LENGTH);

    SHA1_Final((unsigned char*) hash, &ctx);

    int i;
    for(i = 0; i < SHA_DIGEST_LENGTH; i++)
      res[i] = hash[i];

    free(o_key_pad);
    free(i_key_pad);
}

void hotp(char* output, int klen, char* K, int clen, char* C){
  hmac(output, klen, K, clen, C);
}

void totp(char* output, int klen, char* K, int t){
  char* tc = malloc(sizeof(int));

  int i;
  for(i = 0; i < sizeof(int); i++){
    tc[i] = ((unsigned char*) &t)[sizeof(int) - i - 1];
  }

  hotp(output, klen, K, 4, tc);
}

int getTime(int slotSize){
  int t = time(0);
  int remainder = t % slotSize;

  return t - remainder;

}

void str2hex(char** output, int ilen, char* input){

    int i;
    for(i = 0; i < ilen; i++){
      sprintf(*output + 2*i, "%02x", (unsigned char) input[i]);
    }

}

int main(int argc, char* argv[]){

    // char* a = "abc";
    // char* b = "def";
    char* c = malloc(SHA_DIGEST_LENGTH);
    char *res = malloc(2*SHA_DIGEST_LENGTH);

    char* secret = "0c76f310c1f0bde009dd860a5c09cb118e8c8caa26aa542522b824c7d3296c3331b473553e29c9e4";

    int secretLen = strlen(secret);

    while(1){
      
      int t = getTime(30);
      totp(c, secretLen, secret, t);

      int i;
      for(i = 0; i < SHA_DIGEST_LENGTH; i++){
        sprintf(res + 2*i, "%02x",(unsigned char) c[i]);
      }

      // str2hex(&res, SHA_DIGEST_LENGTH, c);

      printf("%s\n", res);
      sleep(5);
    }

    return 0;
}
