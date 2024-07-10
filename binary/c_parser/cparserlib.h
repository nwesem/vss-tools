/**
* (C) 2020 Geotab Inc
* (C) 2018 Volvo Cars
*
* All files and artifacts in this repository are licensed under the
* provisions of the license provided by the LICENSE file in this repository.
*
*
* Parser library for a  C binary format VSS tree.
**/
#include "utils.h"

long VSSReadTree(char* filePath);
void VSSWriteTree(char* filePath, long rootHandle);
int VSSSearchNodes(char* searchPath, long rootNode, int maxFound, searchData_t* searchData, bool anyDepth,  bool leafNodesOnly, int listSize, noScopeList_t* noScopeList, int* validation);
int VSSGetLeafNodesList(long rootNode, char* listFname);
int VSSGetUuidList(long rootNode, char* listFname);

long VSSgetParent(long nodeHandle);
long VSSgetChild(long nodeHandle, int childNo);
int VSSgetNumOfChildren(long nodeHandle);
nodeTypes_t VSSgetType(long nodeHandle);
char* VSSgetDatatype(long nodeHandle);
char* VSSgetName(long nodeHandle);
char* VSSgetUUID(long nodeHandle);
int VSSgetValidation(long nodeHandle);
char* VSSgetDescr(long nodeHandle);
int VSSgetNumOfAllowedElements(long nodeHandle);
char* VSSgetAllowedElement(long nodeHandle, int index);
char* VSSgetUnit(long nodeHandle);
nodeHeader_t* VSSgetHeader(long nodeHandle);
uint8_t getMaxValidation(uint8_t newValidation, uint8_t currentMaxValidation);
uint8_t translateToMatrixIndex(uint8_t index);
