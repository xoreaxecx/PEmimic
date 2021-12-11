# Finds a file-donor according to the selected criteria and transplants its parts.
# Dependencies: pip install colorama
import argparse
import copy
from datetime import date
import operator
import os
import struct
import sys
import time

try:
    from colorama import init, Back
except ImportError:
    print('\n#########################################')
    print('Colorama module not found.')
    print('Colors replaced with brackets "[".')
    print('Use "pip install colorama" to add colors.')
    print('#########################################\n')
    input('Press Enter to continue or Ctrl + C to exit...')

    def init():
        pass

    class Back:
        RED = '['
        GREED = '['
        BLACK = '['
        CYAN = '['
        RESET = ']'


# ---   rich consts   ---
RICH_MARK = b'\x52\x69\x63\x68'  # 1751345490 == 0x68636952 == b'\x52\x69\x63\x68' == b'Rich'
DANS_MARK_B = 1147235923         # 1147235923 == 0x44616e53 == b'\x44\x61\x6e\x53' == b'DanS' big endian
DANS_MARK_L = 1399742788         # 1399742788 == 0x536e6144 == b'\x44\x61\x6e\x53' == b'DanS' little endian
KNOWN_PRODUCT_IDS = {
  0: "Unknown",
  1: "Import0",
  2: "Linker510",
  3: "Cvtomf510",
  4: "Linker600",
  5: "Cvtomf600",
  6: "Cvtres500",
  7: "Utc11_Basic",
  8: "Utc11_C",
  9: "Utc12_Basic",
  10: "Utc12_C",
  11: "Utc12_CPP",
  12: "AliasObj60",
  13: "VisualBasic60",
  14: "Masm613",
  15: "Masm710",
  16: "Linker511",
  17: "Cvtomf511",
  18: "Masm614",
  19: "Linker512",
  20: "Cvtomf512",
  21: "Utc12_C_Std",
  22: "Utc12_CPP_Std",
  23: "Utc12_C_Book",
  24: "Utc12_CPP_Book",
  25: "Implib700",
  26: "Cvtomf700",
  27: "Utc13_Basic",
  28: "Utc13_C",
  29: "Utc13_CPP",
  30: "Linker610",
  31: "Cvtomf610",
  32: "Linker601",
  33: "Cvtomf601",
  34: "Utc12_1_Basic",
  35: "Utc12_1_C",
  36: "Utc12_1_CPP",
  37: "Linker620",
  38: "Cvtomf620",
  39: "AliasObj70",
  40: "Linker621",
  41: "Cvtomf621",
  42: "Masm615",
  43: "Utc13_LTCG_C",
  44: "Utc13_LTCG_CPP",
  45: "Masm620",
  46: "ILAsm100",
  47: "Utc12_2_Basic",
  48: "Utc12_2_C",
  49: "Utc12_2_CPP",
  50: "Utc12_2_C_Std",
  51: "Utc12_2_CPP_Std",
  52: "Utc12_2_C_Book",
  53: "Utc12_2_CPP_Book",
  54: "Implib622",
  55: "Cvtomf622",
  56: "Cvtres501",
  57: "Utc13_C_Std",
  58: "Utc13_CPP_Std",
  59: "Cvtpgd1300",
  60: "Linker622",
  61: "Linker700",
  62: "Export622",
  63: "Export700",
  64: "Masm700",
  65: "Utc13_POGO_I_C",
  66: "Utc13_POGO_I_CPP",
  67: "Utc13_POGO_O_C",
  68: "Utc13_POGO_O_CPP",
  69: "Cvtres700",
  70: "Cvtres710p",
  71: "Linker710p",
  72: "Cvtomf710p",
  73: "Export710p",
  74: "Implib710p",
  75: "Masm710p",
  76: "Utc1310p_C",
  77: "Utc1310p_CPP",
  78: "Utc1310p_C_Std",
  79: "Utc1310p_CPP_Std",
  80: "Utc1310p_LTCG_C",
  81: "Utc1310p_LTCG_CPP",
  82: "Utc1310p_POGO_I_C",
  83: "Utc1310p_POGO_I_CPP",
  84: "Utc1310p_POGO_O_C",
  85: "Utc1310p_POGO_O_CPP",
  86: "Linker624",
  87: "Cvtomf624",
  88: "Export624",
  89: "Implib624",
  90: "Linker710",
  91: "Cvtomf710",
  92: "Export710",
  93: "Implib710",
  94: "Cvtres710",
  95: "Utc1310_C",
  96: "Utc1310_CPP",
  97: "Utc1310_C_Std",
  98: "Utc1310_CPP_Std",
  99: "Utc1310_LTCG_C",
  100: "Utc1310_LTCG_CPP",
  101: "Utc1310_POGO_I_C",
  102: "Utc1310_POGO_I_CPP",
  103: "Utc1310_POGO_O_C",
  104: "Utc1310_POGO_O_CPP",
  105: "AliasObj710",
  106: "AliasObj710p",
  107: "Cvtpgd1310",
  108: "Cvtpgd1310p",
  109: "Utc1400_C",
  110: "Utc1400_CPP",
  111: "Utc1400_C_Std",
  112: "Utc1400_CPP_Std",
  113: "Utc1400_LTCG_C",
  114: "Utc1400_LTCG_CPP",
  115: "Utc1400_POGO_I_C",
  116: "Utc1400_POGO_I_CPP",
  117: "Utc1400_POGO_O_C",
  118: "Utc1400_POGO_O_CPP",
  119: "Cvtpgd1400",
  120: "Linker800",
  121: "Cvtomf800",
  122: "Export800",
  123: "Implib800",
  124: "Cvtres800",
  125: "Masm800",
  126: "AliasObj800",
  127: "PhoenixPrerelease",
  128: "Utc1400_CVTCIL_C",
  129: "Utc1400_CVTCIL_CPP",
  130: "Utc1400_LTCG_MSIL",
  131: "Utc1500_C",
  132: "Utc1500_CPP",
  133: "Utc1500_C_Std",
  134: "Utc1500_CPP_Std",
  135: "Utc1500_CVTCIL_C",
  136: "Utc1500_CVTCIL_CPP",
  137: "Utc1500_LTCG_C",
  138: "Utc1500_LTCG_CPP",
  139: "Utc1500_LTCG_MSIL",
  140: "Utc1500_POGO_I_C",
  141: "Utc1500_POGO_I_CPP",
  142: "Utc1500_POGO_O_C",
  143: "Utc1500_POGO_O_CPP",

  144: "Cvtpgd1500",
  145: "Linker900",
  146: "Export900",
  147: "Implib900",
  148: "Cvtres900",
  149: "Masm900",
  150: "AliasObj900",
  151: "Resource900",

  152: "AliasObj1000",
  154: "Cvtres1000",
  155: "Export1000",
  156: "Implib1000",
  157: "Linker1000",
  158: "Masm1000",

  170: "Utc1600_C",
  171: "Utc1600_CPP",
  172: "Utc1600_CVTCIL_C",
  173: "Utc1600_CVTCIL_CPP",
  174: "Utc1600_LTCG_C ",
  175: "Utc1600_LTCG_CPP",
  176: "Utc1600_LTCG_MSIL",
  177: "Utc1600_POGO_I_C",
  178: "Utc1600_POGO_I_CPP",
  179: "Utc1600_POGO_O_C",
  180: "Utc1600_POGO_O_CPP",

  183: "Linker1010",
  184: "Export1010",
  185: "Implib1010",
  186: "Cvtres1010",
  187: "Masm1010",
  188: "AliasObj1010",

  199: "AliasObj1100",
  201: "Cvtres1100",
  202: "Export1100",
  203: "Implib1100",
  204: "Linker1100",
  205: "Masm1100",

  206: "Utc1700_C",
  207: "Utc1700_CPP",
  208: "Utc1700_CVTCIL_C",
  209: "Utc1700_CVTCIL_CPP",
  210: "Utc1700_LTCG_C ",
  211: "Utc1700_LTCG_CPP",
  212: "Utc1700_LTCG_MSIL",
  213: "Utc1700_POGO_I_C",
  214: "Utc1700_POGO_I_CPP",
  215: "Utc1700_POGO_O_C",
  216: "Utc1700_POGO_O_CPP",

  219: "Cvtres1200",
  220: "Export1200",
  221: "Implib1200",
  222: "Linker1200",
  223: "Masm1200",
  # Speculation
  224: "AliasObj1200",

  237: "Cvtres1210",
  238: "Export1210",
  239: "Implib1210",
  240: "Linker1210",
  241: "Masm1210",
  # Speculation
  242: "Utc1810_C",
  243: "Utc1810_CPP",
  244: "Utc1810_CVTCIL_C",
  245: "Utc1810_CVTCIL_CPP",
  246: "Utc1810_LTCG_C ",
  247: "Utc1810_LTCG_CPP",
  248: "Utc1810_LTCG_MSIL",
  249: "Utc1810_POGO_I_C",
  250: "Utc1810_POGO_I_CPP",
  251: "Utc1810_POGO_O_C",
  252: "Utc1810_POGO_O_CPP",

  255: "Cvtres1400",
  256: "Export1400",
  257: "Implib1400",
  258: "Linker1400",
  259: "Masm1400",

  260: "Utc1900_C",
  261: "Utc1900_CPP",
  # Speculation
  262: "Utc1900_CVTCIL_C",
  263: "Utc1900_CVTCIL_CPP",
  264: "Utc1900_LTCG_C ",
  265: "Utc1900_LTCG_CPP",
  266: "Utc1900_LTCG_MSIL",
  267: "Utc1900_POGO_I_C",
  268: "Utc1900_POGO_I_CPP",
  269: "Utc1900_POGO_O_C",
  270: "Utc1900_POGO_O_CPP"
}


class Options:
    search_rich = True
    search_stamp = True
    search_sign = True
    search_vi = True
    search_dbg = True
    search_res = True

    @staticmethod
    def set_all():
        Options.search_rich = True
        Options.search_stamp = True
        Options.search_sign = True
        Options.search_vi = True
        Options.search_dbg = True
        Options.search_res = True

    @staticmethod
    def disable_all():
        Options.search_rich = False
        Options.search_stamp = False
        Options.search_sign = False
        Options.search_vi = False
        Options.search_dbg = False
        Options.search_res = False

    @staticmethod
    def get_count():
        return Options.search_rich + Options.search_stamp + Options.search_sign + Options.search_vi + Options.search_dbg + Options.search_res

    @staticmethod
    def get_string_options():
        options = []
        if Options.search_rich:
            options.append('rich')
        if Options.search_stamp:
            options.append('timePE')
        if Options.search_sign:
            options.append('sign')
        if Options.search_vi:
            options.append('vi')
        if Options.search_dbg:
            options.append('dbg')
        if Options.search_res:
            options.append('res')
        return '-'.join(options)


class Log:
    __path = ''
    __file = None

    @staticmethod
    def init(path):
        # path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mimic_logs')
        if not os.path.exists(path) or not os.path.isdir(path):
            try:
                os.makedirs(path)
            except Exception as e:
                print(e)
                exit_program(f'Can not create log directory: {path}')
        log_name = f'_mimic_log_{int(time.time())}_{Options.get_string_options()}.txt'
        Log.__path = os.path.join(path, log_name)
        Log.__file = open(Log.__path, 'a', buffering=1)         # 1 means line buffered

    @staticmethod
    def write(message):
        if Log.__file:
            Log.__file.write(f'{message}\n\n')

    # Close log handle
    @staticmethod
    def close():
        if Log.__file:
            Log.__file.close()


class Section:
    def __init__(self, struct_offset, section_struct):
        self.struct_offset = struct_offset
        self.struct_size = 40
        self.bname = section_struct[:8]
        self.vsize = int.from_bytes(section_struct[8:12], 'little')
        self.vaddr = int.from_bytes(section_struct[12:16], 'little')
        self.rsize = int.from_bytes(section_struct[16:20], 'little')
        self.raddr = int.from_bytes(section_struct[20:24], 'little')


class ResDir:
    def __init__(self, struct_offset, struct_bytes):
        self.struct_offset = struct_offset
        self.chracteristics = int.from_bytes(struct_bytes[:4], 'little')
        self.timedatestamp = int.from_bytes(struct_bytes[4:8], 'little')
        self.major_version = int.from_bytes(struct_bytes[8:10], 'little')
        self.minor_version = int.from_bytes(struct_bytes[10:12], 'little')
        self.named_entries_count = int.from_bytes(struct_bytes[12:14], 'little')
        self.id_entries_count = int.from_bytes(struct_bytes[14:16], 'little')
        self.struct_size = 16
        self.vi = None
        self.entries = []

    @property
    def entries_count(self):
        return self.named_entries_count + self.id_entries_count

    @property
    def block_size(self):
        return self.struct_size + self.entries_count * 8

    def to_bytes(self):
        return self.chracteristics.to_bytes(4, 'little') + \
               self.timedatestamp.to_bytes(4, 'little') + \
               self.major_version.to_bytes(2, 'little') + \
               self.minor_version.to_bytes(2, 'little') + \
               self.named_entries_count.to_bytes(2, 'little') + \
               self.id_entries_count.to_bytes(2, 'little')

    def to_flat_struct(self):
        return FlatResDir(chracteristics=self.chracteristics,
                          timedatestamp=self.timedatestamp,
                          major_version=self.major_version,
                          minor_version=self.minor_version,
                          named_entries_count=self.named_entries_count,
                          id_entries_count=self.id_entries_count)


# Contains information only about current entry without trees and leaves.
# Used to reduce memory overhead during resource repackaging.
class FlatResDir:
    def __init__(self, chracteristics, timedatestamp, major_version, minor_version, named_entries_count, id_entries_count):
        self.chracteristics = chracteristics
        self.timedatestamp = timedatestamp
        self.major_version = major_version
        self.minor_version = minor_version
        self.named_entries_count = named_entries_count
        self.id_entries_count = id_entries_count

    def to_bytes(self):
        return self.chracteristics.to_bytes(4, 'little') + \
               self.timedatestamp.to_bytes(4, 'little') + \
               self.major_version.to_bytes(2, 'little') + \
               self.minor_version.to_bytes(2, 'little') + \
               self.named_entries_count.to_bytes(2, 'little') + \
               self.id_entries_count.to_bytes(2, 'little')


class ResDirEntry:
    def __init__(self, struct_offset, struct_size, is_data_next, name_indent, name_offset, entry_bname, entry_id, next_entry_indent, next_entry_offset, next_entry):
        self.struct_offset = struct_offset
        self.struct_size = struct_size
        self.is_data_next = is_data_next
        self.name_indent = name_indent
        self.name_offset = name_offset
        self.bname = entry_bname
        self.id = entry_id
        self.next_entry_indent = next_entry_indent
        self.next_entry_offset = next_entry_offset
        self.entry = next_entry

    def to_bytes(self):
        if self.id is not None:
            name_id_part = self.id.to_bytes(4, 'little')
        else:
            name_id_part = self.name_indent.to_bytes(4, 'little')
        indent_part = self.next_entry_indent.to_bytes(4, 'little')
        return name_id_part + indent_part

    def to_flat_struct(self):
        if self.id is not None:
            name_id = self.id
        else:
            name_id = self.name_indent
        return FlatResDirEntry(name_id=name_id,
                               indent=self.next_entry_indent)


class FlatResDirEntry:
    def __init__(self, name_id, indent):
        self.name_id = name_id
        self.indent = indent

    def to_bytes(self):
        return self.name_id.to_bytes(4, 'little') + \
               self.indent.to_bytes(4, 'little')


class ResDataEntry:
    def __init__(self, struct_offset, struct_size, data_va, data_offset, data_size, code_page, reserved, data_bytes):
        self.struct_offset = struct_offset
        self.struct_size = struct_size
        self.data_va = data_va
        self.data_offset = data_offset
        self.data_size = data_size
        self.code_page = code_page
        self.reserved = reserved
        self.data_bytes = data_bytes

    def to_bytes(self):
        return self.data_va.to_bytes(4, 'little') + \
               self.data_size.to_bytes(4, 'little') + \
               self.code_page.to_bytes(4, 'little') + \
               self.reserved.to_bytes(4, 'little')

    def to_flat_struct(self):
        return FlatResDataEntry(data_va=self.data_va,
                                data_size=self.data_size,
                                code_page=self.code_page,
                                reserved=self.reserved)


class FlatResDataEntry:
    def __init__(self, data_va, data_size, code_page, reserved):
        self.data_va = data_va
        self.data_size = data_size
        self.code_page = code_page
        self.reserved = reserved

    def to_bytes(self):
        return self.data_va.to_bytes(4, 'little') + \
               self.data_size.to_bytes(4, 'little') + \
               self.code_page.to_bytes(4, 'little') + \
               self.reserved.to_bytes(4, 'little')


class FlatResources:
    def __init__(self, struct_entries, name_entries, data_entries, last_indent):
        self.struct_entries = struct_entries
        self.name_entries = name_entries
        self.data_entries = data_entries
        self.last_indent = last_indent


class MimicPart:
    def __init__(self, hdr_offset=None, hdr_size=None, struct_offset=None, struct_size=None, data_offset=None, data_size=None):
        self.hdr_offset = hdr_offset
        self.hdr_size = hdr_size
        self.struct_offset = struct_offset
        self.struct_size = struct_size
        self.data_offset = data_offset
        self.data_size = data_size

    def fits(self, donor_part):
        if self.struct_size is not None and donor_part is not None:
            struct_fits = False
            if donor_part.struct_size is not None:
                struct_fits = self.struct_size >= donor_part.struct_size
            if struct_fits and self.data_size is not None:
                data_fits = False
                if donor_part.data_size is not None:
                    data_fits = self.data_size >= donor_part.data_size
                return struct_fits and data_fits
            else:
                return struct_fits
        return False

    def contains_data(self):
        if self.hdr_offset or self.hdr_size or self.struct_offset or self.struct_size or self.data_offset or self.data_size:
            return True
        else:
            return False


class MimicPE:
    def __init__(self, path_to_file, sections, rich, stamp, sign, dbgs, res, section_alignment=None, file_alignment=None):
        self.path = path_to_file
        self.name = os.path.splitext(os.path.split(path_to_file)[1])[0]
        self.ext = os.path.splitext(os.path.split(path_to_file)[1])[1]
        self.sections = sections
        self.rich = rich
        self.stamp = stamp
        self.sign = sign
        self.dbgs = dbgs
        self.res = res
        self.section_alignment = section_alignment
        self.file_alignment = file_alignment

    def contains_data(self):
        if self.rich or self.stamp or self.sign:
            return True
        else:
            return False

    def count(self):
        return int(self.rich is not None) + int(self.stamp is not None) + int(self.sign is not None) + int(self.dbgs is not None)


class RichParsed:
    def __init__(self, data):
        self.warnings = []
        self.full_length = len(data)
        self.key = data[self.full_length-4:]
        self.checksum = int.from_bytes(self.key, 'little')
        self.raw_data = data[:self.full_length-8]
        self.data_length = len(self.raw_data)
        self.values = self.__get_values_data()

    def __get_values_data(self):
        result = []
        i = 0
        while i < self.data_length:
            result.append(int.from_bytes(self.raw_data[i:i+4], 'little') ^ self.checksum)
            i += 4
        if len(result) % 2:
            err_msg = 'The rich header contains an odd number of values, which may indicate a corrupted structure.'
            print(f'{Back.RED}{err_msg}{Back.RESET}')
        return result[4:]

    def update_key(self):
        self.key = self.checksum.to_bytes(4, 'little')

    def to_bytes(self):
        global DANS_MARK_L, RICH_MARK
        result = [(DANS_MARK_L ^ self.checksum).to_bytes(4, 'little'),
                  self.key,
                  self.key,
                  self.key]
        for v in self.values:
            result.append((v ^ self.checksum).to_bytes(4, 'little'))
        result += [RICH_MARK,
                   self.key]
        return b''.join(result)


def exit_program(message=''):
    if message:
        print(f'{Back.RED}{message}{Back.RESET}')
        Log.write(message)
    Log.close()
    print('Exiting the program...')
    sys.exit(2)


def continue_or_exit_msg(message=''):
    if message:
        print(f'{Back.RED}{message}{Back.RESET}')
        Log.write(message)
    print(f'Press {Back.GREEN}Enter{Back.RESET} to continue or {Back.RED}Ctrl + C{Back.RESET} to exit...')
    try:
        input()
    except KeyboardInterrupt:
        exit_program('Exit with KeyboardInterrupt.')


def get_name_from_offset(data, offset):
    name_size = int.from_bytes(data[offset:offset + 2], 'little') * 2 + 2
    return data[offset:offset + name_size]


def get_offset_rva_delta(sections, rva):
    delta = 0
    for section in sections:
        if section.vaddr <= rva < section.vaddr + section.rsize:
            delta = section.vaddr - section.raddr
            break
    return delta


def merge_resources(fst_res, snd_res, replace_vi, add_resources):
    if replace_vi or add_resources:
        new_res = copy.deepcopy(fst_res)
        if replace_vi:
            if snd_res.vi is not None:
                if new_res.vi is None:
                    new_res.id_entries_count += 1
                new_res.vi = snd_res.vi

        if add_resources:
            for entry in snd_res.entries:
                if entry.id is None:
                    new_res.named_entries_count += 1
                else:
                    new_res.id_entries_count += 1
                new_res.entries.append(entry)
        return new_res


def __resource_offset_is_valid(offset, prev_offsets, eof, checking_original):
    if not 0 < offset < eof:
        if checking_original:
            message = f'Original file contains invalid resource entry.\n' \
                      f'Entry offset: {offset}.\n' \
                      f'EOF: {eof}.\n' \
                      f'Resource analysis terminated.\n' \
                      f'File analysis can be continued without resources.'
            continue_or_exit_msg(message)
        return False

    if offset not in prev_offsets:
        prev_offsets.append(offset)
        return True
    else:
        if checking_original:
            message = f'Original file contains recursive resource pointers.\n' \
                      f'Entry offset: {offset}.\n' \
                      f'Resource analysis terminated.\n' \
                      f'File analysis can be continued without resources.'
            continue_or_exit_msg(message)
        return False


def __get_resource_entries(data, entry_offset, start_offset, offset_va_delta, eof, checking_original, prev_offsets, lvl):
    if lvl > 32:
        if checking_original:
            message = f'Original file contains invalid resource depth.\n' \
                      f'Current depth: {lvl}.\n' \
                      f'Resource analysis terminated.\n' \
                      f'File analysis can be continued without resources.'
            continue_or_exit_msg(message)
        return None
    entry_name_indent = None
    entry_name_offset = None
    entry_bname = None
    entry_id = None

    name_id_bytes = data[entry_offset:entry_offset + 4]
    is_id_entry = name_id_bytes[-1] & 0b10000000 == 0
    if is_id_entry:
        entry_id = int.from_bytes(name_id_bytes, 'little')
    else:
        entry_name_indent = int.from_bytes(name_id_bytes[:-1], 'little')
        entry_name_offset = entry_name_indent + start_offset
        entry_bname = get_name_from_offset(data, entry_name_offset)

    indent_bytes = data[entry_offset + 4:entry_offset + 8]
    next_entry_indent = int.from_bytes(indent_bytes, 'little')
    next_entry_offset = start_offset + int.from_bytes(indent_bytes[:-1], 'little')
    if not __resource_offset_is_valid(next_entry_offset, prev_offsets, eof, checking_original):
        return None

    is_data_next = indent_bytes[-1] & 0b10000000 == 0
    if is_data_next:
        next_entry_struct = data[next_entry_offset:next_entry_offset + 16]
        data_entry_va = int.from_bytes(next_entry_struct[:4], 'little')
        data_entry_offset = data_entry_va - offset_va_delta
        data_entry_size = int.from_bytes(next_entry_struct[4:8], 'little')
        next_entry = ResDataEntry(struct_offset=next_entry_offset,
                                  struct_size=16,
                                  data_va=data_entry_va,
                                  data_offset=data_entry_offset,
                                  data_size=data_entry_size,
                                  code_page=int.from_bytes(next_entry_struct[8:12], 'little'),
                                  reserved=int.from_bytes(next_entry_struct[12:16], 'little'),
                                  data_bytes=data[data_entry_offset:data_entry_offset + data_entry_size])
    else:
        next_entry_struct = data[next_entry_offset:next_entry_offset + 16]
        next_entry = ResDir(next_entry_offset, next_entry_struct)
        i = 0
        fst_offset = next_entry.struct_offset + next_entry.struct_size
        while i < next_entry.entries_count:
            offset = fst_offset + i * 8
            if not __resource_offset_is_valid(offset, prev_offsets, eof, checking_original):
                return None
            entry = __get_resource_entries(data, offset, start_offset, offset_va_delta, eof, checking_original, prev_offsets, lvl=lvl + 1)
            if entry is None:
                return None
            else:
                next_entry.entries.append(entry)
            i += 1

    return ResDirEntry(struct_offset=entry_offset,
                       struct_size=8,
                       is_data_next=is_data_next,
                       name_indent=entry_name_indent,
                       name_offset=entry_name_offset,
                       entry_bname=entry_bname,
                       entry_id=entry_id,
                       next_entry_indent=next_entry_indent,
                       next_entry_offset=next_entry_offset,
                       next_entry=next_entry)


def __get_resource_info(data, res_dir_offset, offset_va_delta, eof, checking_original):
    prev_offsets = []
    res_dir_struct = data[res_dir_offset:res_dir_offset + 16]
    res_dir = ResDir(res_dir_offset, res_dir_struct)
    i = 0
    fst_offset = res_dir.struct_offset + res_dir.struct_size
    while i < res_dir.entries_count:
        offset = fst_offset + i * 8
        if not __resource_offset_is_valid(offset, prev_offsets, eof, checking_original):
            return None

        entry = __get_resource_entries(data, offset, res_dir_offset, offset_va_delta, eof, checking_original, prev_offsets, lvl=0)
        if entry is None:
            return None
        if entry.id is not None and entry.id == 16:
            res_dir.vi = entry
        else:
            res_dir.entries.append(entry)
        i += 1
    return res_dir


def get_level_indents(res_dir, lvl_indents, lvl):
    if lvl in lvl_indents:
        for i in range(lvl, len(lvl_indents)):
            lvl_indents[i] += res_dir.block_size
    else:
        lvl_indents[lvl] = res_dir.block_size
        if lvl > 0:
            lvl_indents[lvl] += lvl_indents[lvl - 1]
    for entry in res_dir.entries:
        if entry.is_data_next:
            next_lvl = lvl + 1
            if next_lvl in lvl_indents:
                lvl_indents[next_lvl] += entry.entry.struct_size
            else:
                lvl_indents[next_lvl] = entry.entry.struct_size
                lvl_indents[next_lvl] += lvl_indents[lvl]
        else:
            get_level_indents(entry.entry, lvl_indents, lvl=lvl + 1)


def __get_flat_entries(res_dir, struct_entries, name_entries, data_entries, lvl_indents, lvl):
    if lvl in struct_entries:
        struct_entries[lvl].append(res_dir.to_flat_struct())
    else:
        struct_entries[lvl] = [res_dir.to_flat_struct()]
    for entry in res_dir.entries:
        struct_entries[lvl].append(entry.to_flat_struct())
        if entry.is_data_next:
            struct_entries[lvl][-1].indent = lvl_indents[lvl]
            lvl_indents[lvl] += entry.entry.struct_size
            next_lvl = lvl + 1
            if next_lvl in struct_entries:
                struct_entries[next_lvl].append(entry.entry.to_flat_struct())
            else:
                struct_entries[next_lvl] = [entry.entry.to_flat_struct()]
            data_entries.append((struct_entries[next_lvl][-1], entry.entry.data_bytes))
        else:
            struct_entries[lvl][-1].indent = lvl_indents[lvl] + 2147483648  # 2147483648 is 80000000 to set high bit
            lvl_indents[lvl] += entry.entry.block_size
            __get_flat_entries(entry.entry, struct_entries, name_entries, data_entries, lvl_indents, lvl=lvl + 1)
        if entry.id is None:
            name_entries.append((struct_entries[lvl][-1], entry.bname))


def get_flat_resources(res_dir):
    struct_entries = {}
    name_entries = []
    data_entries = []
    lvl_indents = {}
    lvl = 0

    if res_dir.vi is not None:
        res_dir.entries.append(res_dir.vi)

    get_level_indents(res_dir, lvl_indents, lvl)
    __get_flat_entries(res_dir, struct_entries, name_entries, data_entries, lvl_indents, lvl)
    return FlatResources(struct_entries=struct_entries,
                         name_entries=name_entries,
                         data_entries=data_entries,
                         last_indent=lvl_indents[list(lvl_indents.keys())[-1]])


def get_resources(data, e_lfanew, is_64, sections, eof, checking_original=False):
    if is_64:
        hdr_offset = e_lfanew + 152  # Resource Directory if PE32+: e_lfanew + 4 + 20 + 128
    else:
        hdr_offset = e_lfanew + 136  # Resource Directory if PE32: e_lfanew + 4 + 20 + 112

    res_dir_vaddr = int.from_bytes(data[hdr_offset:hdr_offset + 4], 'little')
    if res_dir_vaddr == 0:
        if checking_original:
            message = 'Original file does not contain resources.'
            print(f'{Back.CYAN}{message}{Back.RESET}')
            Log.write(message)
        return None

    delta_offset_va = get_offset_rva_delta(sections, res_dir_vaddr)

    res_dir_offset = res_dir_vaddr - delta_offset_va
    if res_dir_offset <= 0 or delta_offset_va == 0:
        if checking_original:
            message = f'Original file contains invalid Resource Directory RVA.\n' \
                      f'Resource Directory RVA:    {res_dir_vaddr}.\n' \
                      f'Resource Directory offset: {res_dir_offset}.\n' \
                      f'Delta offset-va:           {delta_offset_va}.'
            continue_or_exit_msg(message)
        return None
    res_structs = __get_resource_info(data, res_dir_offset, delta_offset_va, eof, checking_original)
    return res_structs


# Returns a bytearray of data with updated checksum
def update_checksum(data):
    e_lfanew = int.from_bytes(data[0x3c:0x40], 'little')
    checksum_offset = e_lfanew + 4 + 20 + 64  # both PE32 and PE32+

    checksum = 0
    remainder = len(data) % 4
    data_len = len(data) + ((4 - remainder) * (remainder != 0))

    for i in range(int(data_len / 4)):
        if i == int(checksum_offset / 4):  # Skip the checksum field
            continue
        if i + 1 == (int(data_len / 4)) and remainder:
            dword = struct.unpack('I', data[i * 4:] + (b'\0' * (4 - remainder)))[0]
        else:
            dword = struct.unpack('I', data[i * 4: i * 4 + 4])[0]
        checksum += dword
        if checksum >= 2 ** 32:
            checksum = (checksum & 0xffffffff) + (checksum >> 32)

    checksum = (checksum & 0xffff) + (checksum >> 16)
    checksum = checksum + (checksum >> 16)
    checksum = checksum & 0xffff
    checksum = checksum + len(data)

    checksum_bytes = checksum.to_bytes(4, 'little')
    return data[:checksum_offset] + checksum_bytes + data[checksum_offset + 4:]


def get_sections(data, e_lfanew, eof, checking_original=False):
    sec_count = int.from_bytes(data[e_lfanew + 6:e_lfanew + 8], 'little')  # NumberOfSections
    sooh = int.from_bytes(data[e_lfanew + 20:e_lfanew + 22], 'little')  # SizeOfOptionalHeader: e_lfanew + 4 + 16
    sec_table_offset = e_lfanew + 24 + sooh  # Section Table: e_lfanew + 4 + 20 + SizeOfOptionalHeader

    if sec_count == 0 or sooh == 0 or sec_table_offset <= 0 or sec_table_offset >= eof:
        if checking_original:
            message = f'Origignal file contains invalid Section struct.\n' \
                      f'NumberOfSections: {sec_count}\n' \
                      f'SizeOfOptionalHeader: {sooh}\n' \
                      f'Section Table offset: {sec_table_offset}'
            exit_program(message)
        return None

    sections = []
    i = sec_count
    while i > 0:
        sections.append(Section(struct_offset=sec_table_offset,
                                section_struct=data[sec_table_offset:sec_table_offset + 40]))
        i -= 1
        sec_table_offset += 40
    if checking_original:
        sections.sort(key=operator.attrgetter('raddr'))
    return tuple(sections)


def change_section_names(data, sections_orig, sections_donor):
    osc = len(sections_orig)    # original section counter
    dsc = len(sections_donor)   # donor section counter
    changes = []
    chg_count = 0

    o = 0
    d = 0
    upd_data = bytearray(data)
    while o < osc:
        if o == osc or d == dsc:
            break
        if sections_orig[o].bname == b'\x2e\x72\x73\x72\x63\x00\x00\x00':  # '.rsrc000'
            o += 1
            continue
        if sections_donor[d].bname == b'\x2e\x72\x73\x72\x63\x00\x00\x00':  # '.rsrc000'
            d += 1
            continue
        if sections_orig[o].bname != sections_donor[d].bname:
            upd_data = upd_data[:sections_orig[o].struct_offset] + sections_donor[d].bname + upd_data[sections_orig[o].struct_offset + 8:]
            donor_sec_str_name = sections_donor[d].bname.decode('UTF-8').rstrip('\x00')
            orig_sec_str_name = sections_orig[o].bname.decode('UTF-8').rstrip('\x00')
            changes.append(f'{orig_sec_str_name} -> {donor_sec_str_name}')
            chg_count += 1
        o += 1
        d += 1
    Log.write("\n".join(changes))
    return tuple([upd_data, f'names_{chg_count}of{osc}'])


def get_rich(data, e_lfanew, checking_original=False):
    RICH = b'\x52\x69\x63\x68'  # 1751345490 == b'\x52\x69\x63\x68' == b'Rich'
    DANS = 1147235923  # 1147235923 == b'\x44\x61\x6e\x53' == b'DanS'
    rich_tail_offset = 0
    rich_head_offset = 0
    rich_xor_key = 0
    j = e_lfanew - 4

    while j >= 0x80:
        if rich_head_offset == 0:
            if data[j:j + 4] == RICH:
                rich_head_offset = j + 8
                rich_xor_key = int.from_bytes(data[j + 4:rich_head_offset], 'big')
                j -= 3
        else:
            if int.from_bytes(data[j:j + 4], 'big') ^ rich_xor_key == DANS:
                rich_tail_offset = j
                break
        j -= 1

    if 0 < rich_tail_offset < rich_head_offset:
        return MimicPart(struct_offset=rich_tail_offset,
                         struct_size=rich_head_offset - rich_tail_offset)
    else:
        if checking_original and rich_tail_offset < rich_head_offset:
            message = 'Original file contains invalid Rich header struct.'
            continue_or_exit_msg(message)
        elif checking_original:
            message = 'Original file does not contain "Rich" header.'
            print(f'{Back.CYAN}{message}{Back.RESET}')
            Log.write(message)
        return None


def _rol(val, num):
    """Rotates val to the left by num bits."""
    return ((val << (num % 32)) & 0xffffffff) | (val >> (32 - (num % 32)))


def get_iat_func_count(data, sections, e_lfanew):
    is_64 = check_64(data, e_lfanew)
    if is_64:
        hdr_offset = e_lfanew + 144  # Import Directory RVA if PE32+: e_lfanew + 4 + 20 + 120
    else:
        hdr_offset = e_lfanew + 128  # Import Directory RVA if PE32: e_lfanew + 4 + 20 + 104
    import_dir_rva = int.from_bytes(data[hdr_offset:hdr_offset + 4], 'little')
    func_count = 0
    if import_dir_rva > 0:
        delta = get_offset_rva_delta(sections, import_dir_rva)

        dll_struct_sz = 20
        dll_empty_struct = b'\x00' * dll_struct_sz
        func_empty_struct = b'\x00\x00\x00\x00'
        dll_offset = import_dir_rva - delta
        dll_struct = data[dll_offset:dll_offset + dll_struct_sz]
        while dll_struct != dll_empty_struct:
            oft = int.from_bytes(dll_struct[0:4], 'little') - delta
            ft = int.from_bytes(dll_struct[16:20], 'little') - delta
            func_offset = ft if ft > 0 else oft
            func_struct = data[func_offset:func_offset + 4]
            while func_struct != func_empty_struct:
                func_count += 1
                func_offset += 4
                func_struct = data[func_offset:func_offset + 4]
            dll_offset += dll_struct_sz
            dll_struct = data[dll_offset:dll_offset + dll_struct_sz]
    return func_count


def fix_rich_linker(data, rich: RichParsed, e_lfanew):
    prodids = []
    for i in range(len(rich.values)):
        if i % 2 == 0:
            prodids.append(rich.values[i] >> 16)

    for prodid in prodids:
        if KNOWN_PRODUCT_IDS.get(prodid) is None:
            continue
        prodid_name = KNOWN_PRODUCT_IDS[prodid]
        if not prodid_name.startswith('Linker'):
            continue

        prodid_name = prodid_name[6:]
        if prodid_name.endswith('p'):
            prodid_name = prodid_name[:-1]
        rich_major = int(prodid_name[:-2])
        rich_minor = int(prodid_name[-2:])

        pe_major_offset = e_lfanew + 26
        pe_minor_offset = e_lfanew + 27
        pe_major_b = data[pe_major_offset: pe_major_offset + 1]
        pe_major_int = int.from_bytes(pe_major_b, 'little')
        pe_minor_b = data[pe_minor_offset: pe_minor_offset + 1]
        pe_minor_int = int.from_bytes(pe_minor_b, 'little')

        if pe_major_int != rich_major or pe_minor_int != rich_minor:
            pe_major_b = rich_major.to_bytes(1, 'little')
            pe_minor_b = rich_minor.to_bytes(1, 'little')
            data = data[:pe_major_offset] + pe_major_b + pe_minor_b + data[pe_minor_offset + 1:]
        break
    return data


def fix_rich_imports(data, rich: RichParsed, sections, e_lfanew):
    iat_count = get_iat_func_count(data, sections, e_lfanew)
    if iat_count > 0:
        rich_iat_count = -1
        val_len = len(rich.values)
        idx = 0
        i = 0
        while i < val_len:
            compid = rich.values[i]
            count = rich.values[i+1]
            if compid == 65536:
                rich_iat_count = count
                idx = i + 1
                break
            i += 2

        if rich_iat_count >= 0:
            rich.values[idx] = iat_count


def fix_rich_checksum(data, start_offset, rich: RichParsed, e_lfanew):
    dos_data = data[:e_lfanew]
    cd = 0
    for i in range(start_offset):
        if 0x3c <= i <= 0x3f:
            cd += _rol(0, i)
        else:
            cd += _rol(dos_data[i], i)

    i = 0
    val_len = len(rich.values)
    cr = 0
    while i < val_len:
        compid = rich.values[i]
        count = rich.values[i+1]
        cr += _rol(compid, count & 0x1f)
        i += 2

    checksum = (start_offset + cd + cr) & 0xffffffff
    if checksum != rich.checksum:
        rich.checksum = checksum
        rich.update_key()


def get_dbg(data, e_lfanew, is_64, sections, eof, checking_original=False):
    if is_64:
        hdr_offset = e_lfanew + 184  # Debug Directory if PE32+: e_lfanew + 4 + 20 + 160
    else:
        hdr_offset = e_lfanew + 168  # Debug Directory if PE32: e_lfanew + 4 + 20 + 144
    struct_vaddr = int.from_bytes(data[hdr_offset:hdr_offset + 4], 'little')
    if struct_vaddr == 0:
        if checking_original:
            message = 'Original file does not contain Debug Directory.'
            print(f'{Back.CYAN}{message}{Back.RESET}')
            Log.write(message)
        return None

    delta_offset_va = get_offset_rva_delta(sections, struct_vaddr)
    struct_offset = struct_vaddr - delta_offset_va
    struct_full_size = int.from_bytes(data[hdr_offset + 4:hdr_offset + 8], 'little')
    if struct_offset <= 0 or struct_offset >= eof or struct_full_size == 0 or struct_full_size % 28 != 0:
        if checking_original:
            message = f'Original file contains invalid Debug Directory struct.\n' \
                      f'Struct VA:        {struct_vaddr}.\n' \
                      f'Struct offset:    {struct_offset}.\n' \
                      f'Struct full size: {struct_full_size}.'
            continue_or_exit_msg(message)
        return None
    struct_count = int.from_bytes(data[hdr_offset + 4:hdr_offset + 8], 'little') // 28

    dbgs = []
    while struct_count > 0:
        check_start = int.from_bytes(data[struct_offset:struct_offset + 4], 'little')
        data_offset = int.from_bytes(data[struct_offset + 24:struct_offset + 28], 'little')
        data_size = int.from_bytes(data[struct_offset + 16:struct_offset + 20], 'little')
        if check_start != 0 or data_offset == 0 or data_offset >= eof or data_size == 0 or data_size >= eof:
            if checking_original:
                message = f'Original file contains invalid Debug Directory entry at {hex(struct_offset)}.\n' \
                          f'Entry check bytes: {check_start}.\n' \
                          f'Entry PointerToRawData: {data_offset}.\n' \
                          f'Entry SizeOfData: {data_size}.'
                continue_or_exit_msg(message)
            return None
        dbgs.append(MimicPart(hdr_offset=hdr_offset,
                              hdr_size=8,
                              struct_offset=struct_offset,
                              struct_size=28,
                              data_offset=data_offset,
                              data_size=data_size))
        struct_count -= 1
        struct_offset += 28
    return dbgs


def get_stamp(data, e_lfanew, checking_original=False):
    tds_offset = e_lfanew + 8
    if data[tds_offset:tds_offset + 4] == b'\x00\x00\x00\x00':
        if checking_original:
            message = 'Original file contains NULL TimeDateStamp.'
            print(f'{Back.CYAN}{message}{Back.RESET}')
            Log.write(message)
        else:
            return None
    return MimicPart(struct_offset=tds_offset,
                     struct_size=4)


def get_sign(data, e_lfanew, is_64, eof, checking_original=False):
    if is_64:
        hdr_offset = e_lfanew + 168  # Security Directory if PE32+: e_lfanew + 4 + 20 + 144
    else:
        hdr_offset = e_lfanew + 152  # Security Directory if PE32: e_lfanew + 4 + 20 + 128
    sign_offset = int.from_bytes(data[hdr_offset:hdr_offset + 4], 'little')
    sign_size = int.from_bytes(data[hdr_offset + 4:hdr_offset + 8], 'little')
    if 0 < sign_offset < eof and 0 < sign_size < eof:
        return MimicPart(hdr_offset=hdr_offset,
                         hdr_size=8,
                         data_offset=sign_offset,
                         data_size=sign_size)
    elif checking_original:
        if sign_offset == 0 and sign_size == 0:
            message = f'Original file does not contain authenticode sign.'
            print(f'{Back.CYAN}{message}{Back.RESET}')
            Log.write(message)
        else:
            message = f'Original file contains invalid authenticode sign struct.\n' \
                      f'Sign offset: {hex(sign_offset)}.\n' \
                      f'Sign size:   {sign_size}.'
            continue_or_exit_msg(message)
        return MimicPart(hdr_offset=hdr_offset,
                         hdr_size=8,
                         data_offset=eof,
                         data_size=sign_size)
    return None


def get_vi(data, e_lfanew, is_64, sections):
    EOF = len(data)
    if is_64:
        res_dir_vaddr = int.from_bytes(data[e_lfanew + 152:e_lfanew + 160], 'little')  # if PE32+: e_lfanew + 4 + 20(file header size) + 128(Resource Directory RVA offset)
    else:
        res_dir_vaddr = int.from_bytes(data[e_lfanew + 136:e_lfanew + 140], 'little')  # if PE32: e_lfanew + 4 + 20(file header size) + 112(Resource Directory RVA offset)
    if res_dir_vaddr <= 0:
        return None

    delta_offset_va = get_offset_rva_delta(sections, res_dir_vaddr)
    if delta_offset_va <= 0:
        return None

    res_dir_offset = res_dir_vaddr - delta_offset_va  # Resource Directory offset
    if res_dir_offset > EOF:
        return None
    id_entries_count = int.from_bytes(data[res_dir_offset + 14:res_dir_offset + 16], 'little')
    if id_entries_count <= 0:
        return None

    named_entries_count = int.from_bytes(data[res_dir_offset + 12:res_dir_offset + 14], 'little')
    entries_count = id_entries_count + named_entries_count

    next_offset_delta = 0
    entry_offset = res_dir_offset + 16
    while entries_count > 0:
        name_id_bytes = data[entry_offset:entry_offset + 4]
        if name_id_bytes[-1] & 0b10000000 == 0:  # if high bit is set to 0, this is id entry, else - named
            entry_id = int.from_bytes(name_id_bytes, 'little')
            if entry_id == 16:  # id == 16 is RT_VERSION
                offset_delta_bytes = data[entry_offset + 4:entry_offset + 8]
                next_offset_delta = int.from_bytes(offset_delta_bytes[:-1], 'little')
                break

        entry_offset += 8
        entries_count -= 1

    if next_offset_delta <= 0:
        return None

    level = 1
    prev_offsets = []
    while True:
        if level > 32:
            return None
        entry_offset = res_dir_offset + next_offset_delta + 16  # 16 is size of resource directory table, entry goes next to it
        if entry_offset not in prev_offsets and entry_offset < EOF:  # check recurcive or invalid refs in resouces
            prev_offsets.append(entry_offset)
        else:
            return None

        offset_delta_bytes = data[entry_offset + 4: entry_offset + 8]
        if offset_delta_bytes[-1] & 0b10000000 == 0:  # resource struct found
            next_offset_delta = int.from_bytes(offset_delta_bytes, 'little')
            if next_offset_delta <= 0:
                return None
            res_struct_offset = res_dir_offset + next_offset_delta
            if res_struct_offset not in prev_offsets and res_struct_offset < EOF:
                prev_offsets.append(res_struct_offset)
                vi_offset = int.from_bytes(data[res_struct_offset:res_struct_offset + 4], 'little') - delta_offset_va
                vi_size = int.from_bytes(data[res_struct_offset + 4:res_struct_offset + 8], 'little')
                if vi_offset == 0 or vi_size == 0:
                    return None
                return MimicPart(struct_offset=res_struct_offset,
                                 struct_size=16,
                                 data_offset=vi_offset,
                                 data_size=vi_size)
            else:
                return None
        else:
            next_offset_delta = int.from_bytes(offset_delta_bytes[:-1], 'little')
            if next_offset_delta <= 0:
                return None
            level += 1


def set_out_path(dst, pe_name):
    today = str(date.today())
    count = 1
    temppath = os.path.join(dst, '_mimic_samples', f'{os.path.splitext(pe_name)[0]}_mimics')
    testsavepath = os.path.join(temppath, f'{today}_{count}')
    while os.path.exists(testsavepath):
        count += 1
        testsavepath = os.path.join(temppath, f'{today}_{count}')
    return testsavepath


def check_args(args):
    if not os.path.exists(args.in_file) or not os.path.isfile(args.in_file):
        exit_program(f'Can not access the "-in" file: {args.in_file}')

    if args.out_dir is None:
        path_parts = os.path.split(args.in_file)
        args.out_dir = set_out_path(path_parts[0], path_parts[1])
    else:
        args.out_dir = set_out_path(args.out_dir, os.path.split(args.in_file)[1])
    if not os.path.exists(args.out_dir):
        try:
            os.makedirs(args.out_dir)
        except Exception as e:
            print(e)
            exit_program(f'Can not create "-out" directory: {args.out_file}')

    if not os.path.exists(args.sd) or not os.path.isdir(args.sd):
        exit_program(f'Can not access the "-sd" directory: {args.sd}')

    if args.limit < 1:
        if args.limit == 0:
            args.limit = sys.maxsize
        else:
            exit_program(f'Invalid value for "-limit": {args.limit}.')

    if args.depth < 0:
        exit_program(f'Invalid value for "-d": {args.d}.')

    if args.no_rich and args.no_timePE and args.no_sign and args.no_vi and args.no_dbg:
        exit_program('All attributes removed, nothing to search.')

    warnings = []
    if args.rich and args.no_rich:
        warnings.append(f'{Back.RED}"-no-rich"{Back.RESET} \tcannot be used at the same time with {Back.GREEN}"-rich"{Back.RESET}.')
    if args.no_rich_fix and args.no_rich or (args.no_rich_fix and not args.rich and any([args.timePE, args.sign, args.vi, args.dbg, args.res])):
        warnings.append(f'{Back.RED}"-no-rich-fix"{Back.RESET} \tcannot be used without {Back.GREEN}"-rich"{Back.RESET}.')
    if args.timePE and args.no_timePE:
        warnings.append(f'{Back.RED}"-no-timePE"{Back.RESET} \tcannot be used at the same time with {Back.GREEN}"-timePE"{Back.RESET}.')
    if args.sign and args.no_sign:
        warnings.append(f'{Back.RED}"-no-sign"{Back.RESET} \tcannot be used at the same time with {Back.RED}"-sign"{Back.RESET}.')
    if args.vi and args.no_vi:
        warnings.append(f'{Back.RED}"-no-vi"{Back.RESET} \tcannot be used at the same time with {Back.GREEN}"-vi"{Back.RESET}.')
    if args.dbg and args.no_dbg:
        warnings.append(f'{Back.RED}"-no-dbg"{Back.RESET} \tcannot be used at the same time with {Back.GREEN}"-dbg"{Back.RESET}.')
    if args.res and args.no_res:
        warnings.append(f'{Back.RED}"-no-res"{Back.RESET} \tcannot be used at the same time with {Back.GREEN}"-res"{Back.RESET}.')

    if warnings:
        print('The following incompatible switches were used:')
        for w in warnings:
            print(f'\t{w}')
        exit_program()

    if args.ext:
        args.ext = tuple(args.ext)
    else:
        args.ext = ('.exe', '.dll')


def set_options(args):
    if (args.rich and args.timePE and args.sign and args.vi and args.dbg and args.res) \
            or (not args.rich and not args.timePE and not args.sign and not args.vi and not args.dbg and not args.res
                and not args.no_rich and not args.no_timePE and not args.no_sign and not args.no_vi and not args.no_dbg and not args.no_res):
        return

    if args.rich or args.timePE or args.sign or args.vi or args.dbg or args.res:
        Options.disable_all()
        if args.rich:
            Options.search_rich = True
        if args.timePE:
            Options.search_stamp = True
        if args.sign:
            Options.search_sign = True
        if args.vi:
            Options.search_vi = True
        if args.dbg:
            Options.search_dbg = True
        if args.res:
            Options.search_res = True
    else:
        if args.no_rich:
            Options.search_rich = False
        if args.no_timePE:
            Options.search_stamp = False
        if args.no_sign:
            Options.search_sign = False
        if args.no_vi:
            Options.search_vi = False
        if args.no_dbg:
            Options.search_dbg = False
        if args.no_res:
            Options.search_res = False
    return


def check_64(data, e_lfanew, checking_original=False):
    magic = data[e_lfanew + 24: e_lfanew + 26]  # magic offset is e_lfanew + 4 + 20(size of file header)
    if magic == b'\x0b\x01':  # b'\x0b\x01' == 0x10B == PE32
        return False
    elif magic == b'\x0b\x02':  # b'\x0b\x02' == 0x20B == PE32+
        return True
    elif checking_original:
        exit_program(f'Original file contains invalid Magic value: {magic}.')
    else:
        return None


def check_original(path_to_file, data, e_lfanew, is_64, orig_eof):
    orig_sections = get_sections(data, e_lfanew, orig_eof, checking_original=True)
    sec_alignment = int.from_bytes(data[e_lfanew + 56:e_lfanew + 60], 'little')  # SectionAlignment offset = e_lfanew + 4 + 20 + 32
    fl_alignment = int.from_bytes(data[e_lfanew + 60:e_lfanew + 64], 'little')   # FileAlignment offset = e_lfanew + 4 + 20 + 36
    if fl_alignment % 2 > 0 or fl_alignment > 64000:
        message = f'Original file contains invalid FileAlignment: {fl_alignment}.\n' \
                  f'FileAlignment is not power of 2 or greater than 64000 (0xFA00).'
        continue_or_exit_msg(message)
    if sec_alignment % 2 > 0:
        message = f'Original file contains invalid SectionAlignment: {sec_alignment}.\n' \
                  f'SectionAlignment is not power of 2.'
        continue_or_exit_msg(message)
    if sec_alignment < fl_alignment:
        message = f'Original file contains invalid FileAlignment or SectionAlignment.\n' \
                  f'FileAlignment: {fl_alignment}.\n' \
                  f'SectionAlignment: {sec_alignment}.\n' \
                  f'SectionAlignment must be greater than FileAlignment'
        continue_or_exit_msg(message)

    if Options.search_rich:
        orig_rich = get_rich(data, e_lfanew, checking_original=True)
        if orig_rich is None:
            Options.search_rich = False
    else:
        orig_rich = None

    if Options.search_dbg:
        orig_dbgs = get_dbg(data, e_lfanew, is_64, orig_sections, orig_eof, checking_original=True)
        if orig_dbgs is None:
            Options.search_dbg = False
    else:
        orig_dbgs = None

    if Options.search_res or Options.search_vi:
        orig_res = get_resources(data, e_lfanew, is_64, orig_sections, orig_eof, checking_original=True)
        if orig_res is None:
            if Options.search_res:
                Options.search_res = False
            if Options.search_vi:
                Options.search_vi = False
                message = 'Due to lack of resource section, can not append VersionInfo.'
                print(f'{Back.CYAN}{message}{Back.RESET}')
                Log.write(message)
        else:
            if Options.search_vi and orig_res.vi is None:
                message = 'Original file does not contain VersionInfo.'
                print(f'{Back.CYAN}{message}{Back.RESET}')
                Log.write(message)
    else:
        orig_res = None

    if Options.get_count() == 0:
        exit_program('Nothing to search.')

    if Options.search_stamp:
        orig_stamp = get_stamp(data, e_lfanew, checking_original=True)
    else:
        orig_stamp = None

    if Options.search_sign:
        orig_sign = get_sign(data, e_lfanew, is_64, orig_eof, checking_original=True)
    else:
        orig_sign = None

    return MimicPE(path_to_file=path_to_file,
                   sections=orig_sections,
                   rich=orig_rich,
                   stamp=orig_stamp,
                   sign=orig_sign,
                   dbgs=orig_dbgs,
                   res=orig_res,
                   section_alignment=sec_alignment,
                   file_alignment=fl_alignment)


parser = argparse.ArgumentParser(description='By default the script includes all attributes for search.')
parser.add_argument('-in', dest='in_file', metavar='path/to/file', required=True, type=str, help='path to input file.')
parser.add_argument('-out', dest='out_dir', metavar='path/to/dir', type=str, default=None, help='path to output dir. "-in" file path is default.')
parser.add_argument('-sd', metavar='search/dir/path', type=str, default=r'C:\Windows', help='path to directory to search. "C:\\Windows" is default.')
parser.add_argument('-d', dest='depth', metavar='depth', type=int, default=5, help='directory search depth. 5 is default.')
parser.add_argument('-limit', metavar='int', type=int, default=0, help='required number of samples to create. all found variants is default. ')
parser.add_argument('-approx', action='store_true', help='use of variants with incomplete match.')
parser.add_argument('-rich', action='store_true', help='adds Rich Header to the search.')
parser.add_argument('-no-rich-fix', dest='no_rich_fix', action='store_true', help='disable modifying Rich Header values.')
parser.add_argument('-no-rich', dest='no_rich', action='store_true', help='removes Rich Header from the search.')
parser.add_argument('-timePE', action='store_true', help='adds TimeDateStamp from File Header to the search.')
parser.add_argument('-no-timePE', dest='no_timePE', action='store_true', help='removes TimeDateStamp from the search.')
parser.add_argument('-sign', action='store_true', help='adds file sign to the search.')
parser.add_argument('-no-sign', dest='no_sign', action='store_true', help='removes file sign from the search.')
parser.add_argument('-vi', action='store_true', help='adds VersionInfo to the search.')
parser.add_argument('-no-vi', dest='no_vi', action='store_true', help='removes VersionInfo from the search.')
parser.add_argument('-res', action='store_true', help='adds resournces to the search.')
parser.add_argument('-no-res', dest='no_res', action='store_true', help='removes resournces from the search.')
parser.add_argument('-dbg', action='store_true', help='adds Debug Directory to the search.')
parser.add_argument('-no-dbg', dest='no_dbg', action='store_true', help='removes Debug Directory from the search.')
parser.add_argument('-ext', metavar='.extension', action='append', default=None,
                    help='file extensions to process. multiple "-ext" supported. Default: ".exe" & ".dll".')
parser.add_argument('-no-checksum', dest='upd_checksum', action='store_false', help='do not update the checksum.')
parser.add_argument('-no-names', dest='change_sec_names', action='store_false', help='do not change section names.')
parser.add_argument('-with-donor', dest='with_donor', action='store_true', help='creates copy of donor in the "-out" directory.')
initargs = parser.parse_args()

init()                                                                           # Colorama initialization
check_args(initargs)                                                             # check for argument conflicts
set_options(initargs)                                                            # set options for search
Log.init(initargs.out_dir)                                                       # Log initialization
Log.write(f'{" ".join(sys.argv)}\nSearch directory: {initargs.sd}\n{"-" * 30}')  # log init settings
counter = 0

with open(initargs.in_file, 'rb') as file:
    orig_data = bytearray(file.read())
pe_eof = len(orig_data)
orig_e_lfanew = int.from_bytes(orig_data[0x3c:0x40], 'little')
if orig_e_lfanew == 0 or orig_e_lfanew >= pe_eof:
    exit_program(f'Original file contains invalid e_lfanew value: {hex(orig_e_lfanew)}.')

pe_is_64 = check_64(orig_data, orig_e_lfanew, checking_original=True)
pe = check_original(initargs.in_file, orig_data, orig_e_lfanew, pe_is_64, pe_eof)
base_level = len(initargs.sd.split("\\"))

for dirpath, dirnames, filenames in os.walk(initargs.sd):
    if initargs.limit == 0:
        break
    cur_level = len(dirpath.split("\\"))
    if cur_level > base_level + initargs.depth:
        continue
    # for filename in [f for f in filenames if f.endswith(".exe") or f.endswith(".dll")]:
    for filename in [f for f in filenames if f.endswith(initargs.ext)]:
        if initargs.limit == 0:
            break

        donor_rich = None
        donor_sign = None
        donor_stamp = None
        donor_dbgs = None
        donor_res = None
        donor_path = os.path.join(dirpath, filename)
        try:
            with open(donor_path, 'rb') as donor_file:
                donor_data = bytearray(donor_file.read())
        except (FileNotFoundError, PermissionError, OSError):
            continue
        donor_eof = len(donor_data)
        donor_e_lfanew = int.from_bytes(donor_data[0x3c:0x40], 'little')
        if donor_e_lfanew == 0 or donor_e_lfanew >= donor_eof:
            continue
        donor_is_64 = check_64(donor_data, donor_e_lfanew)
        if donor_is_64 is None:     # donor_is_64 == None means donor is not valid PE, so go next
            continue

        score = 0
        donor_sections = get_sections(donor_data, donor_e_lfanew, donor_eof)
        if donor_sections is None:
            continue

        if Options.search_rich:
            donor_rich = get_rich(donor_data, donor_e_lfanew)
            if pe.rich.fits(donor_rich):  # check if it fits as there are size restrictions
                score += 1
            else:
                donor_rich = None
        if Options.search_sign:
            donor_sign = get_sign(donor_data, donor_e_lfanew, donor_is_64, donor_eof)
            if donor_sign:
                score += 1
        if Options.search_stamp:
            donor_stamp = get_stamp(donor_data, donor_e_lfanew)
            if donor_stamp:
                score += 1
        if Options.search_dbg:
            donor_dbgs = get_dbg(donor_data, donor_e_lfanew, donor_is_64, donor_sections, donor_eof)
            if donor_dbgs:
                score += 1
        if Options.search_res or Options.search_vi:
            donor_res = get_resources(donor_data, donor_e_lfanew, donor_is_64, donor_sections, donor_eof)
            if Options.search_res and donor_res:
                score += 1
            if Options.search_vi and donor_res and donor_res.vi:
                score += 1

        if score > 0 and score >= Options.get_count() - int(initargs.approx):
            donor = MimicPE(path_to_file=donor_path,
                            sections=donor_sections,
                            rich=donor_rich,
                            stamp=donor_stamp,
                            sign=donor_sign,
                            dbgs=donor_dbgs,
                            res=donor_res)
            new_data = bytearray(orig_data)
            parts = []

            if Options.search_rich and donor.rich:
                parts.append('rich')
                donor_rich_data = donor_data[donor.rich.struct_offset:donor.rich.struct_offset + donor.rich.struct_size]
                if not initargs.no_rich_fix:
                    rich_parsed = RichParsed(donor_rich_data)
                    new_data = fix_rich_linker(new_data, rich_parsed, orig_e_lfanew)
                    fix_rich_imports(new_data, rich_parsed, pe.sections, orig_e_lfanew)
                    fix_rich_checksum(new_data, donor.rich.struct_offset, rich_parsed, orig_e_lfanew)
                new_data = new_data[:pe.rich.struct_offset] + \
                    donor_rich_data + b'\x00' * (pe.rich.struct_size - donor.rich.struct_size) + \
                    new_data[pe.rich.struct_offset + pe.rich.struct_size:]

            if Options.search_stamp and donor.stamp:
                parts.append('timePE')
                new_data = new_data[:pe.stamp.struct_offset] + \
                    donor_data[donor.stamp.struct_offset:donor.stamp.struct_offset + donor.stamp.struct_size] + \
                    new_data[pe.stamp.struct_offset + pe.stamp.struct_size:]

            if Options.search_dbg and donor.dbgs:
                pe.dbgs.sort(key=operator.attrgetter('data_size'))
                donor.dbgs.sort(key=operator.attrgetter('data_size'), reverse=True)
                changed = 0

                for odbg in pe.dbgs:
                    dpc = 0
                    while dpc < len(donor.dbgs):
                        if odbg.fits(donor.dbgs[dpc]):
                            changed += 1
                            ddbg = donor.dbgs.pop(dpc)
                            if odbg.data_size != ddbg.data_size:
                                dbg_entry = donor_data[ddbg.struct_offset:ddbg.struct_offset + 20] + new_data[odbg.struct_offset + 20:odbg.struct_offset + 28]
                                new_data = new_data[:odbg.struct_offset] + dbg_entry + new_data[odbg.struct_offset + odbg.struct_size:]
                            new_data = new_data[:odbg.data_offset] + \
                                donor_data[ddbg.data_offset:ddbg.data_offset + ddbg.data_size] + \
                                b'\x00' * (odbg.data_size - ddbg.data_size) + \
                                new_data[odbg.data_offset + odbg.data_size:]
                            break
                        else:
                            dpc += 1
                parts.append(f'dbg_{changed}of{len(pe.dbgs)}')

            sample_end_of_data = 0
            if (Options.search_res or Options.search_vi) and donor.res:
                if Options.search_res:
                    parts.append('res')
                if Options.search_vi:
                    parts.append('vi')
                merged_res = merge_resources(pe.res, donor.res, Options.search_vi, Options.search_res)
                flat_resources = get_flat_resources(merged_res)

                rsrc_name_entries = bytearray()
                for ne in flat_resources.name_entries:
                    pad = flat_resources.last_indent % 2
                    if pad > 0:
                        rsrc_name_entries += b'\x00'
                        flat_resources.last_indent += 1
                    rsrc_name_entries += ne[1]
                    ne[0].name_id = flat_resources.last_indent + 2147483648  # 2147483648 is 80000000 to set high bit
                    flat_resources.last_indent += len(ne[1])

                rsrc_section = None
                next_sections = []
                for pe_section in pe.sections:
                    if rsrc_section is not None:
                        next_sections.append(pe_section)
                    else:
                        if pe_section.raddr <= pe.res.struct_offset < pe_section.raddr + pe_section.rsize:
                            rsrc_section = pe_section
                rsrc_data_entries = bytearray()
                last_va = rsrc_section.vaddr + flat_resources.last_indent
                for de in flat_resources.data_entries:
                    pad = 4 - last_va % 4  # dword alignment
                    if pad < 4:
                        rsrc_data_entries += b'\x00' * pad
                        last_va += pad
                    rsrc_data_entries += de[1]
                    de[0].data_va = last_va
                    last_va += len(de[1])

                rsrc_struct_entries = bytearray()
                for key in flat_resources.struct_entries:
                    for se in flat_resources.struct_entries[key]:
                        rsrc_struct_entries += se.to_bytes()

                rsrc_bytes = rsrc_struct_entries + rsrc_name_entries + rsrc_data_entries
                rsrc_rsz = len(rsrc_bytes)
                pad = rsrc_rsz % pe.file_alignment
                if pad > 0:
                    rsrc_bytes += (pe.file_alignment - pad) * b'\x00'
                    rsrc_rsz = len(rsrc_bytes)
                sample_end_of_data = rsrc_section.raddr + rsrc_rsz
                if rsrc_rsz != rsrc_section.rsize:

                    # change SizeOfRawData in .rsrc section struct
                    new_data = new_data[:rsrc_section.struct_offset + 16] + rsrc_rsz.to_bytes(4, 'little') + new_data[rsrc_section.struct_offset + 20:]

                    # SizeOfInitializedData offset = e_lfanew + 4 + 20 + 8
                    size_of_init_data = int.from_bytes(new_data[orig_e_lfanew + 32:orig_e_lfanew + 36], 'little')
                    if rsrc_rsz > rsrc_section.rsize:
                        size_of_init_data += rsrc_rsz - rsrc_section.rsize
                    else:
                        size_of_init_data += rsrc_section.rsize - rsrc_rsz

                    # change SizeOfInitializedData
                    new_data = new_data[:orig_e_lfanew + 32] + size_of_init_data.to_bytes(4, 'little') + new_data[orig_e_lfanew + 36:]

                    # change VirtualSize in .rsrc section struct
                    rsrc_vsz = rsrc_section.vsize
                    if rsrc_rsz > rsrc_vsz:
                        rsrc_vsz = rsrc_rsz
                        new_data = new_data[:rsrc_section.struct_offset + 8] + rsrc_vsz.to_bytes(4, 'little') + new_data[rsrc_section.struct_offset + 12:]
                    size_of_image = rsrc_section.vaddr + rsrc_vsz

                    # calculate new addresses for next sections
                    if len(next_sections) > 0:
                        rpointer = rsrc_section.raddr + rsrc_rsz
                        vpointer = rsrc_section.vaddr + rsrc_vsz
                        for ns in next_sections:
                            pad = vpointer % pe.section_alignment
                            if pad > 0:
                                vpointer += pe.section_alignment - pad

                            # change VirtualAddress of next section
                            new_data = new_data[:ns.struct_offset + 12] + vpointer.to_bytes(4, 'little') + new_data[ns.struct_offset + 16:]

                            # change PointerToRawData of next section
                            new_data = new_data[:ns.struct_offset + 20] + rpointer.to_bytes(4, 'little') + new_data[ns.struct_offset + 24:]
                            rpointer += ns.rsize
                            vpointer += ns.vsize

                        # SizeOfImage offset = e_lfanew + 4 + 20 + 56
                        size_of_image = vpointer
                        sample_end_of_data = rpointer

                    # change SizeOfImage
                    new_data = new_data[:orig_e_lfanew + 80] + size_of_image.to_bytes(4, 'little') + new_data[orig_e_lfanew + 84:]
                new_data = new_data[:rsrc_section.raddr] + rsrc_bytes + new_data[rsrc_section.raddr + rsrc_section.rsize:]

            if Options.search_sign and donor.sign:
                parts.append('sign')
                if sample_end_of_data < pe.sign.data_offset:
                    sample_end_of_data = pe.sign.data_offset
                if pe.sign.data_size != donor.sign.data_size:  # change size of data in struct if needed
                    dd_entry = sample_end_of_data.to_bytes(4, 'little') + donor.sign.data_size.to_bytes(4, 'little')
                    new_data = new_data[:pe.sign.hdr_offset] + dd_entry + new_data[pe.sign.hdr_offset + pe.sign.hdr_size:]
                new_data = new_data[:sample_end_of_data] + \
                    donor_data[donor.sign.data_offset:donor.sign.data_offset + donor.sign.data_size] + \
                    new_data[sample_end_of_data + pe.sign.data_size:]

            if initargs.change_sec_names:
                names_result = change_section_names(new_data, pe.sections, donor.sections)
                new_data = names_result[0]
                parts.append(names_result[1])
            if initargs.upd_checksum:
                new_data = update_checksum(new_data)

            counter += 1
            initargs.limit -= 1
            sample_name = f'{str(counter)}_{pe.name}-{donor.name}_{"-".join(parts)}{pe.ext}'
            sample_path = os.path.join(initargs.out_dir, sample_name)
            msg = f'Donor: {donor.path}\nSample: {sample_path}'
            Log.write(msg)
            with open(sample_path, 'wb') as f:
                f.write(new_data)
            print(sample_name)
            if initargs.with_donor:
                donor_name = f'{str(counter)}_{donor.name}{donor.ext}'
                donor_path = os.path.join(initargs.out_dir, donor_name)
                with open(donor_path, 'wb') as f:
                    f.write(donor_data)
            Log.write('----------------------------------------')

if initargs.limit == 0:
    msg = 'Limit reached.'
    print(f'{Back.CYAN}{msg}{Back.RESET}')
    Log.write(msg)

msg = f'Files savad in: {initargs.out_dir}'
print(f'{Back.BLACK}{msg}{Back.RESET}')
Log.write(msg)
Log.close()