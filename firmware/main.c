#include <stdio.h>
#include <stdint.h>

#define RWX_OK 0
#define RWX_ERR -1

struct target_profile {
    char platform[32];
    char model[32];
    char revision[32];
    uint32_t ram_mb;
    uint32_t storage_gb;
    char boot_state[32];
};

static int read_target_profile(struct target_profile *profile) {
    if (!profile) {
        return RWX_ERR;
    }

    snprintf(profile->platform, sizeof(profile->platform), "console");
    snprintf(profile->model, sizeof(profile->model), "unknown");
    snprintf(profile->revision, sizeof(profile->revision), "unknown");
    profile->ram_mb = 0;
    profile->storage_gb = 0;
    snprintf(profile->boot_state, sizeof(profile->boot_state), "recovery");
    return RWX_OK;
}

int main(void) {
    struct target_profile profile = {0};
    if (read_target_profile(&profile) != RWX_OK) {
        printf("Failed to read target profile.\n");
        return 1;
    }

    printf("Platform: %s\n", profile.platform);
    printf("Model: %s\n", profile.model);
    printf("Revision: %s\n", profile.revision);
    printf("RAM: %u MB\n", profile.ram_mb);
    printf("Storage: %u GB\n", profile.storage_gb);
    printf("Boot state: %s\n", profile.boot_state);
    return 0;
}
