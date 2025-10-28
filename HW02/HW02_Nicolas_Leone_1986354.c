#include <openssl/evp.h>
#include <openssl/err.h>
#include <openssl/rand.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h> 

void handle_crypto_error(void) {
    ERR_print_errors_fp(stderr);
    abort();
}

// load file content into memory buffer
int load_file_content(const char *filepath, unsigned char **buffer) {
    FILE *fp = fopen(filepath, "rb");
    if (!fp) {
        perror("Cannot open file");
        return -1;
    }

    // get file size using stat
    struct stat file_info;
    if (stat(filepath, &file_info) != 0) {
        perror("Cannot get file size");
        fclose(fp);
        return -1;
    }

    int size = file_info.st_size;
    *buffer = (unsigned char *)malloc(size);

    if (!*buffer) {
        perror("Memory allocation failed");
        fclose(fp);
        return -1;
    }

    // load file content into buffer
    fread(*buffer, 1, size, fp);
    fclose(fp);
    return size;
}

// save data buffer to file
void save_to_file(const char *filepath, unsigned char *buffer, int buffer_len) {
    FILE *fp = fopen(filepath, "wb");
    fwrite(buffer, 1, buffer_len, fp);
    fclose(fp);
}

// perform encryption using specified cipher
int perform_encryption(const EVP_CIPHER *cipher_algo, unsigned char *input_data, int input_len, unsigned char *secret_key, unsigned char *init_vector, unsigned char *output_data) {
    EVP_CIPHER_CTX *cipher_ctx;
    int bytes_written, total_encrypted;

    if (!(cipher_ctx = EVP_CIPHER_CTX_new())) handle_crypto_error();
    if (1 != EVP_EncryptInit_ex(cipher_ctx, cipher_algo, NULL, secret_key, init_vector)) handle_crypto_error();
    if (1 != EVP_EncryptUpdate(cipher_ctx, output_data, &bytes_written, input_data, input_len)) handle_crypto_error();
    total_encrypted = bytes_written;
    if (1 != EVP_EncryptFinal_ex(cipher_ctx, output_data + bytes_written, &bytes_written)) handle_crypto_error();
    total_encrypted += bytes_written;
    EVP_CIPHER_CTX_free(cipher_ctx);

    return total_encrypted;
}

int perform_decryption(const EVP_CIPHER *cipher_algo, unsigned char *encrypted_data, int encrypted_len, unsigned char *secret_key, unsigned char *init_vector, unsigned char *output_data) {
    EVP_CIPHER_CTX *cipher_ctx;
    int bytes_written, total_decrypted;

    if (!(cipher_ctx = EVP_CIPHER_CTX_new())) handle_crypto_error();
    if (1 != EVP_DecryptInit_ex(cipher_ctx, cipher_algo, NULL, secret_key, init_vector)) handle_crypto_error();
    if (1 != EVP_DecryptUpdate(cipher_ctx, output_data, &bytes_written, encrypted_data, encrypted_len)) handle_crypto_error();
    total_decrypted = bytes_written;
    if (1 != EVP_DecryptFinal_ex(cipher_ctx, output_data + bytes_written, &bytes_written)) handle_crypto_error();
    total_decrypted += bytes_written;
    EVP_CIPHER_CTX_free(cipher_ctx);

    return total_decrypted;
}

void process_file_with_ciphers(const char *input_file, unsigned char *encryption_key) {
    unsigned char *plaintext, *ciphertext, *decryptedtext;
    int plaintext_len, ciphertext_len, decryptedtext_len;
    struct timespec time_start, time_end;

    printf("Processing file: %s\n\n", input_file);

    // load the input file
    plaintext_len = load_file_content(input_file, &plaintext);
    if (plaintext_len < 0) return;

    // allocate memory for encrypted and recovered data
    ciphertext = (unsigned char *)malloc(plaintext_len + EVP_MAX_BLOCK_LENGTH);
    decryptedtext = (unsigned char *)malloc(plaintext_len + EVP_MAX_BLOCK_LENGTH);

    const EVP_CIPHER *cipher_list[] = {EVP_aes_128_cbc(), EVP_sm4_cbc(), EVP_camellia_128_cbc()};
    const char *cipher_names[] = {"AES-128-CBC", "SM4-128-CBC", "Camellia-128-CBC"};

    // test each cipher algorithm
    for (int idx = 0; idx < 3; idx++) {
        unsigned char init_vec[16]; // initialization vector for current cipher

        // generate random initialization vector
        if (RAND_bytes(init_vec, sizeof(init_vec)) != 1) {
            perror("Error generating random bytes for IV");
            free(plaintext);
            free(ciphertext);
            free(decryptedtext);
            return;
        }

        printf("%s Encryption/Decryption:\n", cipher_names[idx]);

        // measure time for encryption operation
        clock_gettime(CLOCK_MONOTONIC, &time_start);
        ciphertext_len = perform_encryption(cipher_list[idx], plaintext, plaintext_len, encryption_key, init_vec, ciphertext);
        clock_gettime(CLOCK_MONOTONIC, &time_end);
        long encryption_time = (time_end.tv_sec - time_start.tv_sec) * 1000000 + (time_end.tv_nsec - time_start.tv_nsec) / 1000;
        printf("Encryption of %s with %s: %ld microseconds\n", input_file, cipher_names[idx], encryption_time);

        // measure time for decryption operation
        clock_gettime(CLOCK_MONOTONIC, &time_start);
        decryptedtext_len = perform_decryption(cipher_list[idx], ciphertext, ciphertext_len, encryption_key, init_vec, decryptedtext);
        clock_gettime(CLOCK_MONOTONIC, &time_end);
        long decryption_time = (time_end.tv_sec - time_start.tv_sec) * 1000000 + (time_end.tv_nsec - time_start.tv_nsec) / 1000;
        printf("Decryption of %s with %s: %ld microseconds\n", input_file, cipher_names[idx], decryption_time);

        decryptedtext[decryptedtext_len] = '\0';  // add null terminator for text data

        // verify decryption correctness
        if (memcmp(plaintext, decryptedtext, plaintext_len) == 0) {
            printf("Decryption successful for %s using %s\n", input_file, cipher_names[idx]);
        } else {
            printf("Decryption failed for %s using %s\n", input_file, cipher_names[idx]);
        }
        printf("\n");
    }

    free(plaintext);
    free(ciphertext);
    free(decryptedtext);
}

int main() {
    unsigned char encryption_key[16]; // 128-bit key

    // generate random 128-bit symmetric key at initialization
    if (RAND_bytes(encryption_key, sizeof(encryption_key)) != 1) {
        fprintf(stderr, "Error generating random key\n");
        ERR_print_errors_fp(stderr);
        return 1;
    }

    printf("Generated 128-bit random key: ");
    for (int i = 0; i < 16; i++) {
        printf("%02x", encryption_key[i]);
    }
    printf("\n--------------------------------------------------\n");

    // process the 16B text file with all cipher algorithms
    process_file_with_ciphers("text_16B.txt", encryption_key);

    printf("--------------------------------------------------\n");

    // process the 20KB text file with all cipher algorithms
    process_file_with_ciphers("text_20KB.txt", encryption_key);

    printf("--------------------------------------------------\n");

    // process the 2MB binary file with all cipher algorithms
    process_file_with_ciphers("binary_2MB.bin", encryption_key);

    return 0;
}
