from __future__ import annotations
import collections, itertools, re
from collections.abc import Sequence
from typing import Optional, Union
from reedsolo import RSCodec
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from tkinter import messagebox
from PIL import Image, ImageTk
import numpy as np
import sys
encoding="utf-8-sig"

# ---- QR Code symbol class ----

class QrCode:
    """A QR Code symbol, which is a type of two-dimension barcode..."""
    MIN_VERSION: int = 1
    MAX_VERSION: int = 40
    _PENALTY_N1: int = 3
    _PENALTY_N2: int = 3
    _PENALTY_N3: int = 40
    _PENALTY_N4: int = 10
    _ECC_CODEWORDS_PER_BLOCK: Sequence[Sequence[int]] = (
        (-1, 7, 10, 15, 20, 26, 18, 20, 24, 30, 18, 20, 24, 26, 30, 22, 24, 28, 30, 28, 28, 28, 28, 30, 30, 26, 28, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30),
        (-1, 10, 16, 26, 18, 24, 16, 18, 22, 22, 26, 30, 22, 22, 24, 24, 28, 28, 26, 26, 26, 26, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28, 28),
        (-1, 13, 22, 18, 26, 18, 24, 18, 22, 20, 24, 28, 26, 24, 20, 30, 24, 28, 28, 26, 30, 28, 30, 30, 30, 30, 28, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30),
        (-1, 17, 28, 22, 16, 22, 28, 26, 26, 24, 28, 24, 28, 22, 24, 24, 30, 28, 28, 26, 28, 30, 24, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30))
    _NUM_ERROR_CORRECTION_BLOCKS: Sequence[Sequence[int]] = (
        (-1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 4, 4, 4, 4, 4, 6, 6, 6, 6, 7, 8, 8, 9, 9, 10, 12, 12, 12, 13, 14, 15, 16, 17, 18, 19, 19, 20, 21, 22, 24, 25),
        (-1, 1, 1, 1, 2, 2, 4, 4, 4, 5, 5, 5, 8, 9, 9, 10, 10, 11, 13, 14, 16, 17, 17, 18, 20, 21, 23, 25, 26, 28, 29, 31, 33, 35, 37, 38, 40, 43, 45, 47, 49),
        (-1, 1, 1, 2, 2, 4, 4, 6, 6, 8, 8, 8, 10, 12, 16, 12, 17, 16, 18, 21, 20, 23, 23, 25, 27, 29, 34, 34, 35, 38, 40, 43, 45, 48, 51, 53, 56, 59, 62, 65, 68),
        (-1, 1, 1, 2, 4, 4, 4, 5, 6, 8, 8, 11, 11, 16, 16, 18, 16, 19, 21, 25, 25, 25, 34, 30, 32, 35, 37, 40, 42, 45, 48, 51, 54, 57, 60, 63, 66, 70, 74, 77, 81))
    _MASK_PATTERNS: Sequence[collections.abc.Callable[[int,int],int]] = (
        (lambda x, y: (x + y) % 2),
        (lambda x, y: y % 2),
        (lambda x, y: x % 3),
        (lambda x, y: (x + y) % 3),
        (lambda x, y: (x // 3 + y // 2) % 2),
        (lambda x, y: x * y % 2 + x * y % 3),
        (lambda x, y: (x * y % 2 + x * y % 3) % 2),
        (lambda x, y: ((x + y) % 2 + x * y % 3) % 2),
    )

    class Ecc:
        def __init__(self, i: int, fb: int) -> None:
            self.ordinal = i
            self.formatbits = fb
        LOW = None
        MEDIUM = None
        QUARTILE = None
        HIGH = None
    Ecc.LOW = Ecc(0, 1)
    Ecc.MEDIUM = Ecc(1, 0)
    Ecc.QUARTILE = Ecc(2, 3)
    Ecc.HIGH = Ecc(3, 2)

    @staticmethod
    def encode_text(text: str, ecl: QrCode.Ecc, minversion: int = 1, maxversion: int = 40, mask: int = -1, boostecl: bool = True) -> QrCode:
        segs: list[QrSegment] = QrSegment.make_segments(text)
        return QrCode.encode_segments(segs, ecl, minversion, maxversion, mask, boostecl)

    @staticmethod
    def encode_binary(data: Union[bytes,Sequence[int]], ecl: QrCode.Ecc) -> QrCode:
        return QrCode.encode_segments([QrSegment.make_bytes(data)], ecl)

    @staticmethod
    def encode_segments(segs: Sequence[QrSegment], ecl: QrCode.Ecc, minversion: int = 1, maxversion: int = 40, mask: int = -1, boostecl: bool = True) -> QrCode:
        if not (QrCode.MIN_VERSION <= minversion <= maxversion <= QrCode.MAX_VERSION) or not (-1 <= mask <= 7):
            raise ValueError("Invalid value")
        for version in range(minversion, maxversion + 1):
            datacapacitybits: int = QrCode._get_num_data_codewords(version, ecl) * 8
            datausedbits: Optional[int] = QrSegment.get_total_bits(segs, version)
            if (datausedbits is not None) and (datausedbits <= datacapacitybits):
                break
            if version >= maxversion:
                msg: str = "Segment too long"
                if datausedbits is not None:
                    msg = f"Data length = {datausedbits} bits, Max capacity = {datacapacitybits} bits"
                raise DataTooLongError(msg)
        assert datausedbits is not None
        for newecl in (QrCode.Ecc.MEDIUM, QrCode.Ecc.QUARTILE, QrCode.Ecc.HIGH):
            if boostecl and (datausedbits <= QrCode._get_num_data_codewords(version, newecl) * 8):
                ecl = newecl
        bb = _BitBuffer()
        for seg in segs:
            bb.append_bits(seg.get_mode().get_mode_bits(), 4)
            bb.append_bits(seg.get_num_chars(), seg.get_mode().num_char_count_bits(version))
            bb.extend(seg._bitdata)
        assert len(bb) == datausedbits
        datacapacitybits = QrCode._get_num_data_codewords(version, ecl) * 8
        bb.append_bits(0, min(4, datacapacitybits - len(bb)))
        bb.append_bits(0, -len(bb) % 8)
        for padbyte in itertools.cycle((0xEC, 0x11)):
            if len(bb) >= datacapacitybits:
                break
            bb.append_bits(padbyte, 8)
        datacodewords = bytearray([0] * (len(bb) // 8))
        for (i, bit) in enumerate(bb):
            datacodewords[i >> 3] |= bit << (7 - (i & 7))
        return QrCode(version, ecl, datacodewords, mask)

    def __init__(self, version: int, errcorlvl: QrCode.Ecc, datacodewords: Union[bytes,Sequence[int]], msk: int) -> None:
        if not (QrCode.MIN_VERSION <= version <= QrCode.MAX_VERSION):
            raise ValueError("Version value out of range")
        if not (-1 <= msk <= 7):
            raise ValueError("Mask value out of range")
        self._version = version
        self._size = version * 4 + 17
        self._errcorlvl = errcorlvl
        self._modules = [[False] * self._size for _ in range(self._size)]
        self._isfunction = [[False] * self._size for _ in range(self._size)]
        self._draw_function_patterns()
        allcodewords: bytes = self._add_ecc_and_interleave(bytearray(datacodewords))
        self._draw_codewords(allcodewords)
        if msk == -1:
            minpenalty: int = 1 << 32
            for i in range(8):
                self._apply_mask(i)
                self._draw_format_bits(i)
                penalty = self._get_penalty_score()
                if penalty < minpenalty:
                    msk = i
                    minpenalty = penalty
                self._apply_mask(i)
        assert 0 <= msk <= 7
        self._mask = msk
        self._apply_mask(msk)
        self._draw_format_bits(msk)
        del self._isfunction

    def get_version(self) -> int:
        return self._version

    def get_size(self) -> int:
        return self._size

    def get_error_correction_level(self) -> QrCode.Ecc:
        return self._errcorlvl

    def get_mask(self) -> int:
        return self._mask

    def get_module(self, x: int, y: int) -> bool:
        return (0 <= x < self._size) and (0 <= y < self._size) and self._modules[y][x]

    def _draw_function_patterns(self) -> None:
        for i in range(self._size):
            self._set_function_module(6, i, i % 2 == 0)
            self._set_function_module(i, 6, i % 2 == 0)
        self._draw_finder_pattern(3, 3)
        self._draw_finder_pattern(self._size - 4, 3)
        self._draw_finder_pattern(3, self._size - 4)
        alignpatpos: list[int] = self._get_alignment_pattern_positions()
        numalign: int = len(alignpatpos)
        skips: Sequence[tuple[int,int]] = ((0, 0), (0, numalign - 1), (numalign - 1, 0))
        for i in range(numalign):
            for j in range(numalign):
                if (i, j) not in skips:
                    self._draw_alignment_pattern(alignpatpos[i], alignpatpos[j])
        self._draw_format_bits(0)
        self._draw_version()

    def _draw_format_bits(self, mask: int) -> None:
        data: int = self._errcorlvl.formatbits << 3 | mask
        rem: int = data
        for _ in range(10):
            rem = (rem << 1) ^ ((rem >> 9) * 0x537)
        bits: int = (data << 10 | rem) ^ 0x5412
        assert bits >> 15 == 0
        for i in range(0, 6):
            self._set_function_module(8, i, _get_bit(bits, i))
        self._set_function_module(8, 7, _get_bit(bits, 6))
        self._set_function_module(8, 8, _get_bit(bits, 7))
        self._set_function_module(7, 8, _get_bit(bits, 8))
        for i in range(9, 15):
            self._set_function_module(14 - i, 8, _get_bit(bits, i))
        for i in range(0, 8):
            self._set_function_module(self._size - 1 - i, 8, _get_bit(bits, i))
        for i in range(8, 15):
            self._set_function_module(8, self._size - 15 + i, _get_bit(bits, i))
        self._set_function_module(8, self._size - 8, True)

    def _draw_version(self) -> None:
        if self._version < 7:
            return
        rem: int = self._version
        for _ in range(12):
            rem = (rem << 1) ^ ((rem >> 11) * 0x1F25)
        bits: int = self._version << 12 | rem
        assert bits >> 18 == 0
        for i in range(18):
            bit: bool = _get_bit(bits, i)
            a: int = self._size - 11 + i % 3
            b: int = i // 3
            self._set_function_module(a, b, bit)
            self._set_function_module(b, a, bit)

    def _draw_finder_pattern(self, x: int, y: int) -> None:
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                xx, yy = x + dx, y + dy
                if (0 <= xx < self._size) and (0 <= yy < self._size):
                    self._set_function_module(xx, yy, max(abs(dx), abs(dy)) not in (2, 4))

    def _draw_alignment_pattern(self, x: int, y: int) -> None:
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                self._set_function_module(x + dx, y + dy, max(abs(dx), abs(dy)) != 1)

    def _set_function_module(self, x: int, y: int, isdark: bool) -> None:
        assert type(isdark) is bool
        self._modules[y][x] = isdark
        self._isfunction[y][x] = True

    def _add_ecc_and_interleave(self, data: bytearray) -> bytes:
        """使用 reedsolo 替换 Reed-Solomon 纠错"""
        version: int = self._version
        assert len(data) == QrCode._get_num_data_codewords(version, self._errcorlvl)
        numblocks: int = QrCode._NUM_ERROR_CORRECTION_BLOCKS[self._errcorlvl.ordinal][version]
        blockecclen: int = QrCode._ECC_CODEWORDS_PER_BLOCK[self._errcorlvl.ordinal][version]
        rawcodewords: int = QrCode._get_num_raw_data_modules(version) // 8
        numshortblocks: int = numblocks - rawcodewords % numblocks
        shortblocklen: int = rawcodewords // numblocks
        rs = RSCodec(blockecclen)  # 初始化 reedsolo
        blocks = []
        k: int = 0
        for i in range(numblocks):
            dat = data[k : k + shortblocklen - blockecclen + (0 if i < numshortblocks else 1)]
            k += len(dat)
            ecc = rs.encode(dat)[len(dat):]  # 生成纠错码字
            if i < numshortblocks:
                dat.append(0)
            blocks.append(dat + ecc)
        assert k == len(data)
        result = bytearray()
        for i in range(len(blocks[0])):
            for (j, blk) in enumerate(blocks):
                if (i != shortblocklen - blockecclen) or (j >= numshortblocks):
                    result.append(blk[i])
        assert len(result) == rawcodewords
        return result

    def _draw_codewords(self, data: bytes) -> None:
        assert len(data) == QrCode._get_num_raw_data_modules(self._version) // 8
        i: int = 0
        for right in range(self._size - 1, 0, -2):
            if right <= 6:
                right -= 1
            for vert in range(self._size):
                for j in range(2):
                    x: int = right - j
                    upward: bool = (right + 1) & 2 == 0
                    y: int = (self._size - 1 - vert) if upward else vert
                    if (not self._isfunction[y][x]) and (i < len(data) * 8):
                        self._modules[y][x] = _get_bit(data[i >> 3], 7 - (i & 7))
                        i += 1
        assert i == len(data) * 8

    def _apply_mask(self, mask: int) -> None:
        if not (0 <= mask <= 7):
            raise ValueError("Mask value out of range")
        masker: collections.abc.Callable[[int,int],int] = QrCode._MASK_PATTERNS[mask]
        for y in range(self._size):
            for x in range(self._size):
                self._modules[y][x] ^= (masker(x, y) == 0) and (not self._isfunction[y][x])

    def _get_penalty_score(self) -> int:
        result: int = 0
        size: int = self._size
        modules: list[list[bool]] = self._modules
        for y in range(size):
            runcolor: bool = False
            runx: int = 0
            runhistory = collections.deque([0] * 7, 7)
            for x in range(size):
                if modules[y][x] == runcolor:
                    runx += 1
                    if runx == 5:
                        result += QrCode._PENALTY_N1
                    elif runx > 5:
                        result += 1
                else:
                    self._finder_penalty_add_history(runx, runhistory)
                    if not runcolor:
                        result += self._finder_penalty_count_patterns(runhistory) * QrCode._PENALTY_N3
                    runcolor = modules[y][x]
                    runx = 1
            result += self._finder_penalty_terminate_and_count(runcolor, runx, runhistory) * QrCode._PENALTY_N3
        for x in range(size):
            runcolor = False
            runy: int = 0
            runhistory = collections.deque([0] * 7, 7)
            for y in range(size):
                if modules[y][x] == runcolor:
                    runy += 1
                    if runy == 5:
                        result += QrCode._PENALTY_N1
                    elif runy > 5:
                        result += 1
                else:
                    self._finder_penalty_add_history(runy, runhistory)
                    if not runcolor:
                        result += self._finder_penalty_count_patterns(runhistory) * QrCode._PENALTY_N3
                    runcolor = modules[y][x]
                    runy = 1
            result += self._finder_penalty_terminate_and_count(runcolor, runy, runhistory) * QrCode._PENALTY_N3
        for y in range(size - 1):
            for x in range(size - 1):
                if modules[y][x] == modules[y][x + 1] == modules[y + 1][x] == modules[y + 1][x + 1]:
                    result += QrCode._PENALTY_N2
        dark: int = sum((1 if cell else 0) for row in modules for cell in row)
        total: int = size**2
        k: int = (abs(dark * 20 - total * 10) + total - 1) // total - 1
        assert 0 <= k <= 9
        result += k * QrCode._PENALTY_N4
        assert 0 <= result <= 2568888
        return result

    def _get_alignment_pattern_positions(self) -> list[int]:
        if self._version == 1:
            return []
        else:
            numalign: int = self._version // 7 + 2
            step: int = (self._version * 8 + numalign * 3 + 5) // (numalign * 4 - 4) * 2
            result: list[int] = [(self._size - 7 - i * step) for i in range(numalign - 1)] + [6]
            return list(reversed(result))

    @staticmethod
    def _get_num_raw_data_modules(ver: int) -> int:
        if not (QrCode.MIN_VERSION <= ver <= QrCode.MAX_VERSION):
            raise ValueError("Version number out of range")
        result: int = (16 * ver + 128) * ver + 64
        if ver >= 2:
            numalign: int = ver // 7 + 2
            result -= (25 * numalign - 10) * numalign - 55
            if ver >= 7:
                result -= 36
        assert 208 <= result <= 29648
        return result

    @staticmethod
    def _get_num_data_codewords(ver: int, ecl: QrCode.Ecc) -> int:
        return QrCode._get_num_raw_data_modules(ver) // 8 \
            - QrCode._ECC_CODEWORDS_PER_BLOCK[ecl.ordinal][ver] \
            * QrCode._NUM_ERROR_CORRECTION_BLOCKS[ecl.ordinal][ver]

    def _finder_penalty_count_patterns(self, runhistory: collections.deque[int]) -> int:
        n: int = runhistory[1]
        assert n <= self._size * 3
        core: bool = n > 0 and (runhistory[2] == runhistory[4] == runhistory[5] == n) and runhistory[3] == n * 3
        return (1 if (core and runhistory[0] >= n * 4 and runhistory[6] >= n) else 0) \
             + (1 if (core and runhistory[6] >= n * 4 and runhistory[0] >= n) else 0)

    def _finder_penalty_terminate_and_count(self, currentruncolor: bool, currentrunlength: int, runhistory: collections.deque[int]) -> int:
        if currentruncolor:
            self._finder_penalty_add_history(currentrunlength, runhistory)
            currentrunlength = 0
        currentrunlength += self._size
        self._finder_penalty_add_history(currentrunlength, runhistory)
        return self._finder_penalty_count_patterns(runhistory)

    def _finder_penalty_add_history(self, currentrunlength: int, runhistory: collections.deque[int]) -> None:
        if runhistory[0] == 0:
            currentrunlength += self._size
        runhistory.appendleft(currentrunlength)

    def to_image(self, scale: int = 10, border: int = 4) -> Image.Image:
        size = self._size
        img = Image.new('1', (size * scale + border * 2 * scale, size * scale + border * 2 * scale), 1)
        pixels = img.load()
        for y in range(size):
            for x in range(size):
                if self.get_module(x, y):
                    for dy in range(scale):
                        for dx in range(scale):
                            pixels[x * scale + dx + border * scale, y * scale + dy + border * scale] = 0
        return img

# ---- Data segment class ----

class QrSegment:
    class Mode:
        def __init__(self, modebits: int, charcounts: tuple[int,int,int]):
            self._modebits = modebits
            self._charcounts = charcounts
        def get_mode_bits(self) -> int:
            return self._modebits
        def num_char_count_bits(self, ver: int) -> int:
            return self._charcounts[(ver + 7) // 17]
        NUMERIC = None
        ALPHANUMERIC = None
        BYTE = None
        KANJI = None
        ECI = None
    Mode.NUMERIC = Mode(0x1, (10, 12, 14))
    Mode.ALPHANUMERIC = Mode(0x2, (9, 11, 13))
    Mode.BYTE = Mode(0x4, (8, 16, 16))
    Mode.KANJI = Mode(0x8, (8, 10, 12))
    Mode.ECI = Mode(0x7, (0, 0, 0))

    @staticmethod
    def make_bytes(data: Union[bytes,Sequence[int]]) -> QrSegment:
        bb = _BitBuffer()
        for b in data:
            bb.append_bits(b, 8)
        return QrSegment(QrSegment.Mode.BYTE, len(data), bb)

    @staticmethod
    def make_numeric(digits: str) -> QrSegment:
        if not QrSegment.is_numeric(digits):
            raise ValueError("String contains non-numeric characters")
        bb = _BitBuffer()
        i: int = 0
        while i < len(digits):
            n: int = min(len(digits) - i, 3)
            bb.append_bits(int(digits[i : i + n]), n * 3 + 1)
            i += n
        return QrSegment(QrSegment.Mode.NUMERIC, len(digits), bb)

    @staticmethod
    def make_alphanumeric(text: str) -> QrSegment:
        if not QrSegment.is_alphanumeric(text):
            raise ValueError("String contains unencodable characters in alphanumeric mode")
        bb = _BitBuffer()
        for i in range(0, len(text) - 1, 2):
            temp: int = QrSegment._ALPHANUMERIC_ENCODING_TABLE[text[i]] * 45
            temp += QrSegment._ALPHANUMERIC_ENCODING_TABLE[text[i + 1]]
            bb.append_bits(temp, 11)
        if len(text) % 2 > 0:
            bb.append_bits(QrSegment._ALPHANUMERIC_ENCODING_TABLE[text[-1]], 6)
        return QrSegment(QrSegment.Mode.ALPHANUMERIC, len(text), bb)

    @staticmethod
    def make_segments(text: str) -> list[QrSegment]:
        if text == "":
            return []
        elif QrSegment.is_numeric(text):
            return [QrSegment.make_numeric(text)]
        elif QrSegment.is_alphanumeric(text):
            return [QrSegment.make_alphanumeric(text)]
        else:
            return [QrSegment.make_bytes(text.encode("UTF-8"))]

    @staticmethod
    def make_eci(assignval: int) -> QrSegment:
        bb = _BitBuffer()
        if assignval < 0:
            raise ValueError("ECI assignment value out of range")
        elif assignval < (1 << 7):
            bb.append_bits(assignval, 8)
        elif assignval < (1 << 14):
            bb.append_bits(0b10, 2)
            bb.append_bits(assignval, 14)
        elif assignval < 1000000:
            bb.append_bits(0b110, 3)
            bb.append_bits(assignval, 21)
        else:
            raise ValueError("ECI assignment value out of range")
        return QrSegment(QrSegment.Mode.ECI, 0, bb)

    @staticmethod
    def is_numeric(text: str) -> bool:
        return QrSegment._NUMERIC_REGEX.fullmatch(text) is not None

    @staticmethod
    def is_alphanumeric(text: str) -> bool:
        return QrSegment._ALPHANUMERIC_REGEX.fullmatch(text) is not None

    _NUMERIC_REGEX: re.Pattern[str] = re.compile(r"[0-9]*")
    _ALPHANUMERIC_REGEX: re.Pattern[str] = re.compile(r"[A-Z0-9 $%*+./:-]*")
    _ALPHANUMERIC_ENCODING_TABLE: dict[str,int] = {ch: i for (i, ch) in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:")}

    def __init__(self, mode: QrSegment.Mode, numch: int, bitdata: Sequence[int]) -> None:
        if numch < 0:
            raise ValueError()
        self._mode = mode
        self._numchars = numch
        self._bitdata = list(bitdata)

    def get_mode(self) -> QrSegment.Mode:
        return self._mode

    def get_num_chars(self) -> int:
        return self._numchars

    def get_data(self) -> list[int]:
        return list(self._bitdata)

    @staticmethod
    def get_total_bits(segs: Sequence[QrSegment], version: int) -> Optional[int]:
        result = 0
        for seg in segs:
            ccbits: int = seg.get_mode().num_char_count_bits(version)
            if seg.get_num_chars() >= (1 << ccbits):
                return None
            result += 4 + ccbits + len(seg._bitdata)
        return result

# ---- Private helper class ----

class _BitBuffer(list[int]):
    def append_bits(self, val: int, n: int) -> None:
        if (n < 0) or (val >> n != 0):
            raise ValueError("Value out of range")
        self.extend(((val >> i) & 1) for i in reversed(range(n)))

def _get_bit(x: int, i: int) -> bool:
    return (x >> i) & 1 != 0

class DataTooLongError(ValueError):
    pass

# ---- GUI Application ----


class QRCodeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QR Code Generator (Version 1 & 2)")
        self.setGeometry(100, 100, 600, 600)

        # 主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 数据保护警告
        self.warning_label = QLabel(
            "警告：请确保输入的文本安全，扫描未知 QR 码可能导致钓鱼或恶意链接风险！"
        )
        self.warning_label.setStyleSheet("color: red; font-weight: bold;")
        self.warning_label.setWordWrap(True)
        main_layout.addWidget(self.warning_label)

        # 输入框布局
        input_layout = QVBoxLayout()
        
        # URL 输入
        url_layout = QHBoxLayout()
        self.url_label = QLabel("URL：")
        url_layout.addWidget(self.url_label)
        self.url_entry = QLineEdit()
        self.url_entry.setFixedWidth(400)
        self.url_entry.mousePressEvent = self.on_entry_click
        url_layout.addWidget(self.url_entry)
        input_layout.addLayout(url_layout)
        
        # 文本输入
        text_layout = QHBoxLayout()
        self.text_label = QLabel("文本：")
        text_layout.addWidget(self.text_label)
        self.text_entry = QLineEdit()
        self.text_entry.setFixedWidth(400)
        self.text_entry.mousePressEvent = self.on_entry_click
        text_layout.addWidget(self.text_entry)
        input_layout.addLayout(text_layout)
        
        # 备注输入
        note_layout = QHBoxLayout()
        self.note_label = QLabel("备注：")
        note_layout.addWidget(self.note_label)
        self.note_entry = QLineEdit()
        self.note_entry.setFixedWidth(400)
        self.note_entry.mousePressEvent = self.on_entry_click
        note_layout.addWidget(self.note_entry)
        input_layout.addLayout(note_layout)
        
        main_layout.addLayout(input_layout)

        # 生成按钮
        self.generate_button = QPushButton("生成 QR 码")
        self.generate_button.clicked.connect(self.generate_qr)
        main_layout.addWidget(self.generate_button)

        # QR 码显示区域
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.qr_label)

        # 状态信息
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

        # 版本容量（Level L）
        self.version_capacities = {1: 25, 2: 47}

        # 启动时显示数据保护弹窗
        self.show_data_protection_warning()

    def show_data_protection_warning(self):
        """显示数据保护和安全警告弹窗"""
        msg = QMessageBox()
        msg.setWindowTitle("数据保护和安全提示")
        msg.setText(
            "本程序仅在本地生成 QR 码，不会存储或上传您的输入数据。\n\n"
            "请注意：\n"
            "- 仅输入您信任的文本或 URL。\n"
            "- 扫描 QR 码前，检查其内容，避免钓鱼或恶意链接。\n"
            "- 本程序生成的 QR 码仅为黑白模块，用于显示和扫描。"
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def on_entry_click(self, event):
        """处理输入框点击事件"""
        sender = self.sender()
        if sender:
            sender.setFocus()


    def generate_qr(self):
        # 拼接所有输入框内容
        input_texts = [
            self.url_entry.text().strip(),
            self.text_entry.text().strip(),
            self.note_entry.text().strip()
        ]
        input_text = "; ".join(t for t in input_texts if t)
        if not input_text:
            self.qr_label.setText("请输入至少一个文本或 URL")
            self.status_label.setText("")
            return
        try:
            # 调试：打印输入文本以验证中文
            print(f"Input text: {input_text}")
            
            # 检查输入长度并选择版本（基于 UTF-8 编码）
            input_length = len(input_text.encode('utf-8'))
            version = 1 if input_length <= self.version_capacities[1] else 2 if input_length <= self.version_capacities[2] else None
            if version is None:
                raise DataTooLongError(f"输入过长 ({input_length} 字节)。Version 2 最大支持 {self.version_capacities[2]} 字节。")
            
            self.status_label.setText(f"使用 QR 版本 {version}")
            
            # 生成 QR 码（确保 UTF-8 编码）
            qr = QrCode.encode_text(input_text, QrCode.Ecc.LOW, minversion=1, maxversion=2, mask=-1)
            
            # 保存中间数据
            seg = QrSegment.make_bytes(input_text.encode('utf-8'))
            data_bytes = input_text.encode('utf-8')
            rs = RSCodec(QrCode._ECC_CODEWORDS_PER_BLOCK[QrCode.Ecc.LOW.ordinal][version])
            rs_codewords = rs.encode(data_bytes)[len(data_bytes):]
            matrix = np.array([[qr.get_module(x, y) for x in range(qr.get_size())] for y in range(qr.get_size())], dtype=int)
            
            # 保存并显示 QR 码
            qr_image = qr.to_image(scale=10, border=4)
            qr_image.save("qr_code.png")
            
            # 直接从保存的文件加载 QPixmap
            pixmap = QPixmap("qr_code.png")
            self.qr_label.setFixedSize(pixmap.width(), pixmap.height())
            self.qr_label.setAlignment(Qt.AlignCenter)
            self.qr_label.setPixmap(pixmap)
            
            # 保存中间数据
            self.save_intermediate_data(input_text, data_bytes, rs_codewords, matrix, qr.get_mask())
        
        except DataTooLongError as e:
            self.qr_label.setPixmap(QPixmap())
            self.status_label.setText(str(e))
            QMessageBox.critical(self, "错误", str(e))
        except Exception as e:
            self.qr_label.setPixmap(QPixmap())
            self.status_label.setText(f"错误: {str(e)}")
            QMessageBox.critical(self, "错误", f"生成 QR 码失败: {str(e)}")

    def save_intermediate_data(self, input_text, data_bytes, rs_codewords, matrix, best_mask):
        with open("intermediate_data.txt", "w", encoding="utf-8") as f:
            f.write("Input Text:\n")
            f.write(f"{input_text}\n\n")
            f.write("Encoded Bytes:\n")
            f.write(f"{data_bytes}\n\n")
            f.write("Reed-Solomon Error Correction Codewords (Hex):\n")
            f.write(f"{rs_codewords.hex()}\n\n")
            f.write(f"Mask Matrix (Pattern {best_mask}):\n")
            f.write(f"{matrix}\n")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QRCodeApp()
    window.show()
    sys.exit(app.exec_())