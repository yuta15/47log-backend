"""訪問記録で使用する都道府県の定義。"""

from enum import IntEnum


class Prefecture(IntEnum):
    """都道府県コードで日本の47都道府県を表す。"""

    HOKKAIDO = 1
    AOMORI = 2
    IWATE = 3
    MIYAGI = 4
    AKITA = 5
    YAMAGATA = 6
    FUKUSHIMA = 7
    IBARAKI = 8
    TOCHIGI = 9
    GUNMA = 10
    SAITAMA = 11
    CHIBA = 12
    TOKYO = 13
    KANAGAWA = 14
    NIIGATA = 15
    TOYAMA = 16
    ISHIKAWA = 17
    FUKUI = 18
    YAMANASHI = 19
    NAGANO = 20
    GIFU = 21
    SHIZUOKA = 22
    AICHI = 23
    MIE = 24
    SHIGA = 25
    KYOTO = 26
    OSAKA = 27
    HYOGO = 28
    NARA = 29
    WAKAYAMA = 30
    TOTTORI = 31
    SHIMANE = 32
    OKAYAMA = 33
    HIROSHIMA = 34
    YAMAGUCHI = 35
    TOKUSHIMA = 36
    KAGAWA = 37
    EHIME = 38
    KOCHI = 39
    FUKUOKA = 40
    SAGA = 41
    NAGASAKI = 42
    KUMAMOTO = 43
    OITA = 44
    MIYAZAKI = 45
    KAGOSHIMA = 46
    OKINAWA = 47
