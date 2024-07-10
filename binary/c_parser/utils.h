/**
 * (C) 2020 Geotab Inc
 * (C) 2018 Volvo Cars
 *
 * All files and artifacts in this repository are licensed under the
 * provisions of the license provided by the LICENSE file in this repository.
 *
 *
 * Parser library for a C binary format VSS tree.
 **/
#include <stdint.h>

#define UNKNOWN 0
typedef enum {SENSOR=1, ACTUATOR, ATTRIBUTE, BRANCH, STRUCT, PROPERTY } nodeTypes_t;

#define MAXALLOWEDELEMENTLEN 64
typedef char allowed_t[MAXALLOWEDELEMENTLEN];

typedef struct extendedAttr_t extendedAttr_t; // forward declaration needed to point to next attribute

typedef struct extendedAttr_t {
    char* name;
    char* value;
    struct extendedAttr_t* next;
} extendedAttr_t;

typedef struct nodeHeader_t {
    uint8_t amountExtendedAttr;
    struct extendedAttr_t* extendedAttr;
} nodeHeader_t;

typedef struct node_t {
    uint8_t headerLen;
    nodeHeader_t* header;
    uint16_t nameLen;
    char* name;
    nodeTypes_t type;
    uint8_t uuidLen;
    char* uuid;
    uint16_t descrLen;
    char* description;
    uint8_t datatypeLen;
    char* datatype;
    uint8_t maxLen;
    char* max;
    uint8_t minLen;
    char* min;
    uint8_t unitLen;
    char* unit;
    uint8_t allowed;
    allowed_t *allowedDef;
    uint8_t defaultLen;
    char* defaultAllowed;
    uint8_t validate;
    uint8_t children;
    struct node_t* parent;
    struct node_t** child;
} node_t;

#define MAXCHARSPATH 512
typedef char path_t[MAXCHARSPATH];

#define MAXFOUNDNODES 1500   //may need to be revised when tree size grows
typedef struct searchData_t {
    path_t responsePaths;
    long foundNodeHandles;
} searchData_t;

typedef struct noScopeList_t {
    path_t path;
} noScopeList_t;
