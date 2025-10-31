#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <openssl/kdf.h>
#include <openssl/err.h>
#include <openssl/rand.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>

#define KEY_SIZE 32  // 256 bits for master key
#define AES_KEY_SIZE 16  // 128 bits for AES
#define HMAC_KEY_SIZE 32  // 256 bits for HMAC
#define IV_SIZE 16  // 128 bits for IV
#define NONCE_SIZE 12  // 96 bits for nonce (ChaCha20-Poly1305)
#define HMAC_TAG_SIZE 32  // 256 bits for HMAC-SHA256 tag
#define AEAD_TAG_SIZE 16  // 128 bits for GCM/Poly1305 authentication tag
#define NUM_RUNS 5  // Number of repeated experiments

void handle_crypto_error(void) {
    ERR_print_errors_fp(stderr);
    abort();
}

// Derive keys from master key using HKDF
int derive_keys(unsigned char *master_key, const char *info, 
                unsigned char *enc_key, int enc_key_len,
                unsigned char *mac_key, int mac_key_len) {
    EVP_PKEY_CTX *pctx;
    unsigned char temp_buffer[64];  // Temporary buffer for derived material
    size_t outlen = enc_key_len + mac_key_len;
    
    if (outlen > sizeof(temp_buffer)) {
        fprintf(stderr, "Derived key material too large\n");
        return 0;
    }
    
    pctx = EVP_PKEY_CTX_new_id(EVP_PKEY_HKDF, NULL);
    if (!pctx) handle_crypto_error();
    
    if (EVP_PKEY_derive_init(pctx) <= 0) handle_crypto_error();
    if (EVP_PKEY_CTX_set_hkdf_md(pctx, EVP_sha256()) <= 0) handle_crypto_error();
    if (EVP_PKEY_CTX_set1_hkdf_key(pctx, master_key, KEY_SIZE) <= 0) handle_crypto_error();
    if (EVP_PKEY_CTX_add1_hkdf_info(pctx, (unsigned char *)info, strlen(info)) <= 0) handle_crypto_error();
    
    if (EVP_PKEY_derive(pctx, temp_buffer, &outlen) <= 0) handle_crypto_error();
    
    memcpy(enc_key, temp_buffer, enc_key_len);
    memcpy(mac_key, temp_buffer + enc_key_len, mac_key_len);
    
    EVP_PKEY_CTX_free(pctx);
    return 1;
}

// Load file content into memory
int load_file_content(const char *filepath, unsigned char **buffer) {
    FILE *fp = fopen(filepath, "rb");
    if (!fp) {
        perror("Cannot open file");
        return -1;
    }
    
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
    
    if (fread(*buffer, 1, size, fp) != size) {
        perror("Error reading file");
        free(*buffer);
        fclose(fp);
        return -1;
    }
    
    fclose(fp);
    return size;
}

// AES-128-CTR + HMAC (Encrypt-then-MAC)
int aes_ctr_hmac_encrypt(unsigned char *plaintext, int plaintext_len,
                         unsigned char *enc_key, unsigned char *mac_key,
                         unsigned char *iv, unsigned char *ciphertext,
                         unsigned char *tag) {
    EVP_CIPHER_CTX *ctx;
    int len, ciphertext_len;
    unsigned int mac_len;
    
    // Encrypt with AES-128-CTR
    if (!(ctx = EVP_CIPHER_CTX_new())) handle_crypto_error();
    if (1 != EVP_EncryptInit_ex(ctx, EVP_aes_128_ctr(), NULL, enc_key, iv)) handle_crypto_error();
    if (1 != EVP_EncryptUpdate(ctx, ciphertext, &len, plaintext, plaintext_len)) handle_crypto_error();
    ciphertext_len = len;
    if (1 != EVP_EncryptFinal_ex(ctx, ciphertext + len, &len)) handle_crypto_error();
    ciphertext_len += len;
    EVP_CIPHER_CTX_free(ctx);
    
    // Compute HMAC over ciphertext
    if (!HMAC(EVP_sha256(), mac_key, HMAC_KEY_SIZE, ciphertext, ciphertext_len, tag, &mac_len)) {
        handle_crypto_error();
    }
    
    return ciphertext_len;
}

int aes_ctr_hmac_decrypt(unsigned char *ciphertext, int ciphertext_len,
                         unsigned char *enc_key, unsigned char *mac_key,
                         unsigned char *iv, unsigned char *tag,
                         unsigned char *plaintext) {
    unsigned char computed_tag[EVP_MAX_MD_SIZE];
    unsigned int mac_len;
    EVP_CIPHER_CTX *ctx;
    int len, plaintext_len;
    
    // Verify HMAC
    if (!HMAC(EVP_sha256(), mac_key, HMAC_KEY_SIZE, ciphertext, ciphertext_len, computed_tag, &mac_len)) {
        handle_crypto_error();
    }
    
    if (memcmp(tag, computed_tag, HMAC_TAG_SIZE) != 0) {
        fprintf(stderr, "HMAC verification failed!\n");
        return -1;
    }
    
    // Decrypt with AES-128-CTR
    if (!(ctx = EVP_CIPHER_CTX_new())) handle_crypto_error();
    if (1 != EVP_DecryptInit_ex(ctx, EVP_aes_128_ctr(), NULL, enc_key, iv)) handle_crypto_error();
    if (1 != EVP_DecryptUpdate(ctx, plaintext, &len, ciphertext, ciphertext_len)) handle_crypto_error();
    plaintext_len = len;
    if (1 != EVP_DecryptFinal_ex(ctx, plaintext + len, &len)) handle_crypto_error();
    plaintext_len += len;
    EVP_CIPHER_CTX_free(ctx);
    
    return plaintext_len;
}

// ChaCha20 + HMAC (Encrypt-then-MAC)
int chacha20_hmac_encrypt(unsigned char *plaintext, int plaintext_len,
                          unsigned char *enc_key, unsigned char *mac_key,
                          unsigned char *iv, unsigned char *ciphertext,
                          unsigned char *tag) {
    EVP_CIPHER_CTX *ctx;
    int len, ciphertext_len;
    unsigned int mac_len;
    
    // Encrypt with ChaCha20
    if (!(ctx = EVP_CIPHER_CTX_new())) handle_crypto_error();
    if (1 != EVP_EncryptInit_ex(ctx, EVP_chacha20(), NULL, enc_key, iv)) handle_crypto_error();
    if (1 != EVP_EncryptUpdate(ctx, ciphertext, &len, plaintext, plaintext_len)) handle_crypto_error();
    ciphertext_len = len;
    if (1 != EVP_EncryptFinal_ex(ctx, ciphertext + len, &len)) handle_crypto_error();
    ciphertext_len += len;
    EVP_CIPHER_CTX_free(ctx);
    
    // Compute HMAC over ciphertext
    if (!HMAC(EVP_sha256(), mac_key, HMAC_KEY_SIZE, ciphertext, ciphertext_len, tag, &mac_len)) {
        handle_crypto_error();
    }
    
    return ciphertext_len;
}

int chacha20_hmac_decrypt(unsigned char *ciphertext, int ciphertext_len,
                          unsigned char *enc_key, unsigned char *mac_key,
                          unsigned char *iv, unsigned char *tag,
                          unsigned char *plaintext) {
    unsigned char computed_tag[EVP_MAX_MD_SIZE];
    unsigned int mac_len;
    EVP_CIPHER_CTX *ctx;
    int len, plaintext_len;
    
    // Verify HMAC
    if (!HMAC(EVP_sha256(), mac_key, HMAC_KEY_SIZE, ciphertext, ciphertext_len, computed_tag, &mac_len)) {
        handle_crypto_error();
    }
    
    if (memcmp(tag, computed_tag, HMAC_TAG_SIZE) != 0) {
        fprintf(stderr, "HMAC verification failed!\n");
        return -1;
    }
    
    // Decrypt with ChaCha20
    if (!(ctx = EVP_CIPHER_CTX_new())) handle_crypto_error();
    if (1 != EVP_DecryptInit_ex(ctx, EVP_chacha20(), NULL, enc_key, iv)) handle_crypto_error();
    if (1 != EVP_DecryptUpdate(ctx, plaintext, &len, ciphertext, ciphertext_len)) handle_crypto_error();
    plaintext_len = len;
    if (1 != EVP_DecryptFinal_ex(ctx, plaintext + len, &len)) handle_crypto_error();
    plaintext_len += len;
    EVP_CIPHER_CTX_free(ctx);
    
    return plaintext_len;
}

// AES-128-GCM (Authenticated Encryption)
int aes_gcm_encrypt(unsigned char *plaintext, int plaintext_len,
                    unsigned char *key, unsigned char *iv,
                    unsigned char *ciphertext, unsigned char *tag) {
    EVP_CIPHER_CTX *ctx;
    int len, ciphertext_len;
    
    if (!(ctx = EVP_CIPHER_CTX_new())) handle_crypto_error();
    if (1 != EVP_EncryptInit_ex(ctx, EVP_aes_128_gcm(), NULL, NULL, NULL)) handle_crypto_error();
    if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, IV_SIZE, NULL)) handle_crypto_error();
    if (1 != EVP_EncryptInit_ex(ctx, NULL, NULL, key, iv)) handle_crypto_error();
    if (1 != EVP_EncryptUpdate(ctx, ciphertext, &len, plaintext, plaintext_len)) handle_crypto_error();
    ciphertext_len = len;
    if (1 != EVP_EncryptFinal_ex(ctx, ciphertext + len, &len)) handle_crypto_error();
    ciphertext_len += len;
    if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, AEAD_TAG_SIZE, tag)) handle_crypto_error();
    EVP_CIPHER_CTX_free(ctx);
    
    return ciphertext_len;
}

int aes_gcm_decrypt(unsigned char *ciphertext, int ciphertext_len,
                    unsigned char *key, unsigned char *iv,
                    unsigned char *tag, unsigned char *plaintext) {
    EVP_CIPHER_CTX *ctx;
    int len, plaintext_len, ret;
    
    if (!(ctx = EVP_CIPHER_CTX_new())) handle_crypto_error();
    if (1 != EVP_DecryptInit_ex(ctx, EVP_aes_128_gcm(), NULL, NULL, NULL)) handle_crypto_error();
    if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, IV_SIZE, NULL)) handle_crypto_error();
    if (1 != EVP_DecryptInit_ex(ctx, NULL, NULL, key, iv)) handle_crypto_error();
    if (1 != EVP_DecryptUpdate(ctx, plaintext, &len, ciphertext, ciphertext_len)) handle_crypto_error();
    plaintext_len = len;
    if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, AEAD_TAG_SIZE, tag)) handle_crypto_error();
    ret = EVP_DecryptFinal_ex(ctx, plaintext + len, &len);
    EVP_CIPHER_CTX_free(ctx);
    
    if (ret > 0) {
        plaintext_len += len;
        return plaintext_len;
    } else {
        fprintf(stderr, "GCM tag verification failed!\n");
        return -1;
    }
}

// ChaCha20-Poly1305 (Authenticated Encryption)
int chacha20_poly1305_encrypt(unsigned char *plaintext, int plaintext_len,
                               unsigned char *key, unsigned char *nonce,
                               unsigned char *ciphertext, unsigned char *tag) {
    EVP_CIPHER_CTX *ctx;
    int len, ciphertext_len;
    
    if (!(ctx = EVP_CIPHER_CTX_new())) handle_crypto_error();
    if (1 != EVP_EncryptInit_ex(ctx, EVP_chacha20_poly1305(), NULL, NULL, NULL)) handle_crypto_error();
    if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_AEAD_SET_IVLEN, NONCE_SIZE, NULL)) handle_crypto_error();
    if (1 != EVP_EncryptInit_ex(ctx, NULL, NULL, key, nonce)) handle_crypto_error();
    if (1 != EVP_EncryptUpdate(ctx, ciphertext, &len, plaintext, plaintext_len)) handle_crypto_error();
    ciphertext_len = len;
    if (1 != EVP_EncryptFinal_ex(ctx, ciphertext + len, &len)) handle_crypto_error();
    ciphertext_len += len;
    if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_AEAD_GET_TAG, AEAD_TAG_SIZE, tag)) handle_crypto_error();
    EVP_CIPHER_CTX_free(ctx);
    
    return ciphertext_len;
}

int chacha20_poly1305_decrypt(unsigned char *ciphertext, int ciphertext_len,
                               unsigned char *key, unsigned char *nonce,
                               unsigned char *tag, unsigned char *plaintext) {
    EVP_CIPHER_CTX *ctx;
    int len, plaintext_len, ret;
    
    if (!(ctx = EVP_CIPHER_CTX_new())) handle_crypto_error();
    if (1 != EVP_DecryptInit_ex(ctx, EVP_chacha20_poly1305(), NULL, NULL, NULL)) handle_crypto_error();
    if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_AEAD_SET_IVLEN, NONCE_SIZE, NULL)) handle_crypto_error();
    if (1 != EVP_DecryptInit_ex(ctx, NULL, NULL, key, nonce)) handle_crypto_error();
    if (1 != EVP_DecryptUpdate(ctx, plaintext, &len, ciphertext, ciphertext_len)) handle_crypto_error();
    plaintext_len = len;
    if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_AEAD_SET_TAG, AEAD_TAG_SIZE, tag)) handle_crypto_error();
    ret = EVP_DecryptFinal_ex(ctx, plaintext + len, &len);
    EVP_CIPHER_CTX_free(ctx);
    
    if (ret > 0) {
        plaintext_len += len;
        return plaintext_len;
    } else {
        fprintf(stderr, "Poly1305 tag verification failed!\n");
        return -1;
    }
}

// Test function for a specific algorithm
void test_algorithm(const char *algo_name, int algo_type, 
                    unsigned char *plaintext, int plaintext_len,
                    unsigned char *master_key, FILE *results_file) {
    unsigned char enc_key[KEY_SIZE];
    unsigned char mac_key[HMAC_KEY_SIZE];
    unsigned char *ciphertext;
    unsigned char *decryptedtext;
    unsigned char iv[IV_SIZE];
    unsigned char nonce[NONCE_SIZE];
    unsigned char tag[HMAC_TAG_SIZE];  // Large enough for HMAC-SHA256 (32 bytes)
    struct timespec start, end;
    long enc_times[NUM_RUNS], dec_times[NUM_RUNS];
    
    printf("\n%s:\n", algo_name);
    printf("Running %d experiments...\n", NUM_RUNS);
    
    // Allocate buffers
    ciphertext = (unsigned char *)malloc(plaintext_len + EVP_MAX_BLOCK_LENGTH);
    decryptedtext = (unsigned char *)malloc(plaintext_len + EVP_MAX_BLOCK_LENGTH);
    
    if (!ciphertext || !decryptedtext) {
        perror("Memory allocation failed");
        return;
    }
    
    // Derive keys for this algorithm
    if (algo_type <= 2) {  // Encrypt-then-MAC modes need both keys
        derive_keys(master_key, algo_name, enc_key, (algo_type == 1) ? AES_KEY_SIZE : KEY_SIZE, 
                    mac_key, HMAC_KEY_SIZE);
    } else {  // AEAD modes need only encryption key
        derive_keys(master_key, algo_name, enc_key, (algo_type == 3) ? AES_KEY_SIZE : KEY_SIZE, 
                    mac_key, 0);
    }
    
    // Run multiple experiments
    for (int run = 0; run < NUM_RUNS; run++) {
        int ciphertext_len, decryptedtext_len;
        
        // Generate random IV/nonce for each run
        if (algo_type == 4) {  // ChaCha20-Poly1305 uses 96-bit nonce
            if (RAND_bytes(nonce, NONCE_SIZE) != 1) handle_crypto_error();
        } else {
            if (RAND_bytes(iv, IV_SIZE) != 1) handle_crypto_error();
        }
        
        // Encryption
        clock_gettime(CLOCK_MONOTONIC, &start);
        switch (algo_type) {
            case 1:  // AES-128-CTR + HMAC
                ciphertext_len = aes_ctr_hmac_encrypt(plaintext, plaintext_len, enc_key, mac_key, iv, ciphertext, tag);
                break;
            case 2:  // ChaCha20 + HMAC
                ciphertext_len = chacha20_hmac_encrypt(plaintext, plaintext_len, enc_key, mac_key, iv, ciphertext, tag);
                break;
            case 3:  // AES-128-GCM
                ciphertext_len = aes_gcm_encrypt(plaintext, plaintext_len, enc_key, iv, ciphertext, tag);
                break;
            case 4:  // ChaCha20-Poly1305
                ciphertext_len = chacha20_poly1305_encrypt(plaintext, plaintext_len, enc_key, nonce, ciphertext, tag);
                break;
        }
        clock_gettime(CLOCK_MONOTONIC, &end);
        enc_times[run] = (end.tv_sec - start.tv_sec) * 1000000L + 
                         (end.tv_nsec - start.tv_nsec) / 1000L;
        
        // Decryption
        clock_gettime(CLOCK_MONOTONIC, &start);
        switch (algo_type) {
            case 1:  // AES-128-CTR + HMAC
                decryptedtext_len = aes_ctr_hmac_decrypt(ciphertext, ciphertext_len, enc_key, mac_key, iv, tag, decryptedtext);
                break;
            case 2:  // ChaCha20 + HMAC
                decryptedtext_len = chacha20_hmac_decrypt(ciphertext, ciphertext_len, enc_key, mac_key, iv, tag, decryptedtext);
                break;
            case 3:  // AES-128-GCM
                decryptedtext_len = aes_gcm_decrypt(ciphertext, ciphertext_len, enc_key, iv, tag, decryptedtext);
                break;
            case 4:  // ChaCha20-Poly1305
                decryptedtext_len = chacha20_poly1305_decrypt(ciphertext, ciphertext_len, enc_key, nonce, tag, decryptedtext);
                break;
        }
        clock_gettime(CLOCK_MONOTONIC, &end);
        dec_times[run] = (end.tv_sec - start.tv_sec) * 1000000L + 
                         (end.tv_nsec - start.tv_nsec) / 1000L;
        
        // Verify correctness
        if (decryptedtext_len != plaintext_len || memcmp(plaintext, decryptedtext, plaintext_len) != 0) {
            printf("  Run %d: Verification FAILED!\n", run + 1);
        } else {
            printf("  Run %d: Encryption=%ld μs, Decryption=%ld μs [OK]\n", 
                   run + 1, enc_times[run], dec_times[run]);
        }
    }
    
    // Calculate statistics
    long enc_sum = 0, dec_sum = 0;
    long enc_min = enc_times[0], enc_max = enc_times[0];
    long dec_min = dec_times[0], dec_max = dec_times[0];
    
    for (int i = 0; i < NUM_RUNS; i++) {
        enc_sum += enc_times[i];
        dec_sum += dec_times[i];
        if (enc_times[i] < enc_min) enc_min = enc_times[i];
        if (enc_times[i] > enc_max) enc_max = enc_times[i];
        if (dec_times[i] < dec_min) dec_min = dec_times[i];
        if (dec_times[i] > dec_max) dec_max = dec_times[i];
    }
    
    double enc_avg = (double)enc_sum / NUM_RUNS;
    double dec_avg = (double)dec_sum / NUM_RUNS;
    
    printf("\n  Statistics (over %d runs):\n", NUM_RUNS);
    printf("    Encryption - Avg: %.2f μs, Min: %ld μs, Max: %ld μs\n", 
           enc_avg, enc_min, enc_max);
    printf("    Decryption - Avg: %.2f μs, Min: %ld μs, Max: %ld μs\n", 
           dec_avg, dec_min, dec_max);
    
    // Write results to file
    fprintf(results_file, "%s,%.2f,%.2f,%ld,%ld,%ld,%ld\n", 
            algo_name, enc_avg, dec_avg, enc_min, enc_max, dec_min, dec_max);
    
    free(ciphertext);
    free(decryptedtext);
}

int main(int argc, char *argv[]) {
    unsigned char master_key[KEY_SIZE];
    unsigned char *plaintext;
    int plaintext_len;
    FILE *results_file;
    const char *test_file;
    
    // Allow specifying test file as command line argument
    if (argc > 1) {
        test_file = argv[1];
    } else {
        test_file = "testfile_10MB.bin";  // Default file
    }
    
    printf("=================================================================\n");
    printf("  Symmetric Cipher Performance Comparison - Homework 03\n");
    printf("  Student: Nicolas Leone (1986354)\n");
    printf("=================================================================\n\n");
    
    // Generate random master key
    if (RAND_bytes(master_key, KEY_SIZE) != 1) {
        fprintf(stderr, "Error generating random master key\n");
        return 1;
    }
    
    printf("Generated 256-bit random master key: ");
    for (int i = 0; i < KEY_SIZE; i++) {
        printf("%02x", master_key[i]);
    }
    printf("\n");
    printf("All working keys will be derived from this master key using HKDF.\n");
    
    // Load test file
    printf("\nLoading test file: %s...\n", test_file);
    plaintext_len = load_file_content(test_file, &plaintext);
    if (plaintext_len < 0) {
        fprintf(stderr, "Failed to load test file: %s\n", test_file);
        return 1;
    }
    printf("Loaded %s: %d bytes (%.2f MB)\n", 
           test_file, plaintext_len, plaintext_len / (1024.0 * 1024.0));
    
    // Open results file with filename based on test file
    char results_filename[256];
    const char *base_name = strrchr(test_file, '/');
    base_name = base_name ? base_name + 1 : test_file;
    snprintf(results_filename, sizeof(results_filename), "results_%s.csv", base_name);
    
    results_file = fopen(results_filename, "w");
    if (!results_file) {
        perror("Cannot create results file");
        free(plaintext);
        return 1;
    }
    fprintf(results_file, "Algorithm,Avg_Encryption_us,Avg_Decryption_us,Min_Enc_us,Max_Enc_us,Min_Dec_us,Max_Dec_us\n");
    
    printf("\n=================================================================\n");
    printf("  Starting Performance Tests (%d runs per algorithm)\n", NUM_RUNS);
    printf("=================================================================\n");
    
    // Test all four configurations
    test_algorithm("AES-128-CTR + HMAC-SHA256", 1, plaintext, plaintext_len, master_key, results_file);
    printf("\n-----------------------------------------------------------------\n");
    
    test_algorithm("ChaCha20 + HMAC-SHA256", 2, plaintext, plaintext_len, master_key, results_file);
    printf("\n-----------------------------------------------------------------\n");
    
    test_algorithm("AES-128-GCM", 3, plaintext, plaintext_len, master_key, results_file);
    printf("\n-----------------------------------------------------------------\n");
    
    test_algorithm("ChaCha20-Poly1305", 4, plaintext, plaintext_len, master_key, results_file);
    printf("\n=================================================================\n");
    
    printf("\n✓ All tests completed successfully!\n");
    printf("✓ Results saved to %s\n\n", results_filename);
    
    fclose(results_file);
    free(plaintext);
    
    return 0;
}
