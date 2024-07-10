#!/usr/bin/env python3

# Copyright (c) 2022 Contributors to COVESA
#
# This program and the accompanying materials are made available under the
# terms of the Mozilla Public License 2.0 which is available at
# https://www.mozilla.org/en-US/MPL/2.0/
#
# SPDX-License-Identifier: MPL-2.0

# Convert vspec tree to binary format

import argparse
import logging
import ctypes
import os.path
from typing import Optional
from vss_tools.vspec.model.vsstree import VSSNode, VSSType
from vss_tools.vspec.vss2x import Vss2X
from vss_tools.vspec.vspec2vss_config import Vspec2VssConfig

out_file = ""
_cbinary = None


class extendedAttr_t(ctypes.Structure):
    _fields_ = [
        ("nameLen", ctypes.c_uint8),
        ("name", ctypes.c_char_p),
        ("valueLen", ctypes.c_uint8),
        ("value", ctypes.c_char_p),
    ]

class nodeHeader_t(ctypes.Structure):
    _fields_ = [
        ("amountExtendedAttr", ctypes.c_uint8),
        ("extendedAttr", ctypes.POINTER(extendedAttr_t)),
    ]

def createBinaryCnode(fname, header, nodename, nodetype, uuid, description, nodedatatype, nodemin, nodemax, unit, allowed,
                      defaultAllowed, validate, children):
    global _cbinary
    _cbinary.createBinaryCnode(fname, header, nodename, nodetype, uuid, description, nodedatatype, nodemin, nodemax, unit,
                               allowed, defaultAllowed, validate, children)


def allowedString(allowedList):
    allowedStr = ""
    for elem in allowedList:
        allowedStr += hexAllowedLen(elem) + elem
#    print("allowedstr=" + allowedStr + "\n")
    return allowedStr


def hexAllowedLen(allowed):
    hexDigit1 = len(allowed) // 16
    hexDigit2 = len(allowed) - hexDigit1*16
#    print("Hexdigs:" + str(hexDigit1) + str(hexDigit2))
    return "".join([intToHexChar(hexDigit1), intToHexChar(hexDigit2)])


def intToHexChar(hexInt):
    if (hexInt < 10):
        return chr(hexInt + ord('0'))
    else:
        return chr(hexInt - 10 + ord('A'))


def export_node(node, generate_uuid, out_file):
    header = nodeHeader_t()
    header.amountExtendedAttr = len(node.extended_attributes.keys())

    for key, value in node.extended_attributes.items():
        print(f"[python]\t{key=}, {value=}")
        extended_attr = extendedAttr_t()
        extended_attr.nameLen = len(str(key))
        extended_attr.name = str(key).encode('utf-8')
        extended_attr.valueLen = len(str(value))
        extended_attr.value = str(value).encode('utf-8')
        header.extendedAttr = ctypes.pointer(extended_attr)

    nodename = str(node.name)
    b_nodename = nodename.encode('utf-8')

    nodetype = str(node.type.value)
    b_nodetype = nodetype.encode('utf-8')

    nodedescription = str(node.description)
    b_nodedescription = nodedescription.encode('utf-8')

    children = len(node.children)

    nodedatatype = ""
    nodemin = ""
    nodemax = ""
    nodeunit = ""
    nodeallowed = ""
    nodedefault = ""
    nodeuuid = ""
    nodevalidate = ""  # exported to binary

    if node.type == VSSType.SENSOR or node.type == VSSType.ACTUATOR or node.type == VSSType.ATTRIBUTE:
        nodedatatype = str(node.datatype.value)
    b_nodedatatype = nodedatatype.encode('utf-8')

    # many optional attributes are initilized to "" in vsstree.py
    if node.min != "":
        nodemin = str(node.min)
    b_nodemin = nodemin.encode('utf-8')

    if node.max != "":
        nodemax = str(node.max)
    b_nodemax = nodemax.encode('utf-8')

    if node.allowed != "":
        nodeallowed = allowedString(node.allowed)
    b_nodeallowed = nodeallowed.encode('utf-8')

    if node.default != "":
        nodedefault = str(node.default)
    b_nodedefault = nodedefault.encode('utf-8')

    # in case of unit or aggregate, the attribute will be missing
    try:
        nodeunit = str(node.unit.value)
    except AttributeError:
        pass
    b_nodeunit = nodeunit.encode('utf-8')

    if generate_uuid:
        nodeuuid = node.uuid
    b_nodeuuid = nodeuuid.encode('utf-8')

    if "validate" in node.extended_attributes:
        nodevalidate = node.extended_attributes["validate"]
    b_nodevalidate = nodevalidate.encode('utf-8')

    b_fname = out_file.encode('utf-8')

    print(f"[python]\t{header.amountExtendedAttr=}")

    createBinaryCnode(b_fname, header, b_nodename, b_nodetype, b_nodeuuid, b_nodedescription, b_nodedatatype, b_nodemin,
                      b_nodemax, b_nodeunit, b_nodeallowed, b_nodedefault, b_nodevalidate, children)

    for child in node.children:
        export_node(child, generate_uuid, out_file)


class Vss2Binary(Vss2X):

    def __init__(self, vspec2vss_config: Vspec2VssConfig):
        vspec2vss_config.type_tree_supported = False
        vspec2vss_config.no_expand_option_supported = False

    def generate(self, config: argparse.Namespace, root: VSSNode, vspec2vss_config: Vspec2VssConfig,
                 data_type_root: Optional[VSSNode] = None) -> None:
        global _cbinary
        dllName = "../../../../binary/binarytool.so"
        dllAbsPath = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + dllName
        if not os.path.isfile(dllAbsPath):
            logging.error("The required library binarytool.so is not available, exiting!")
            logging.info("You must build the library, "
                         "see https://github.com/COVESA/vss-tools/blob/master/binary/README.md!")
            return
        _cbinary = ctypes.CDLL(dllAbsPath)

        _cbinary.createBinaryCnode.argtypes = (
            ctypes.c_char_p, # fname
            nodeHeader_t,  # header
            ctypes.c_char_p, # nodename
            ctypes.c_char_p, # nodetype
            ctypes.c_char_p, # uuid
            ctypes.c_char_p, # description
            ctypes.c_char_p, # nodedatatype
            ctypes.c_char_p, # nodemin
            ctypes.c_char_p, # nodemax
            ctypes.c_char_p, # unit
            ctypes.c_char_p, # allowed
            ctypes.c_char_p, # defaultAllowed
            ctypes.c_char_p, # validate
            ctypes.c_int  # children
        )

        logging.info("Generating binary output...")
        out_file = config.output_file
        export_node(root, vspec2vss_config.generate_uuid, out_file)
        logging.info("Binary output generated in " + out_file)
