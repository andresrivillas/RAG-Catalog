import logging
import re
from typing import Optional

logger = logging.getLogger("smart_catalog.query_understanding")


def detect_capacity(tokens: list[str], raw_text: str) -> Optional[dict]:
    result: dict = {}
    text = raw_text.lower()

    vol_ml = _detect_ml(text, tokens)
    if vol_ml is not None:
        result["volume_ml"] = vol_ml

    vol_oz = _detect_oz(text, tokens)
    if vol_oz is not None:
        result["volume_oz"] = vol_oz

    litros = _detect_litros(text, tokens)
    if litros is not None:
        ml_from_l = litros * 1000
        if "volume_ml" not in result:
            result["volume_ml"] = ml_from_l
        else:
            result["volume_ml"] = max(result["volume_ml"], ml_from_l)

    mah = _detect_mah(text, tokens)
    if mah is not None:
        result["battery_mah"] = mah

    return result if result else None


def _detect_ml(text: str, tokens: list[str]) -> Optional[int]:
    m = re.search(r"(\d+)\s*ml", text)
    if m:
        val = int(m.group(1))
        logger.debug("Capacidad detectada: %d ml", val)
        return val
    for t in tokens:
        m2 = re.match(r"(\d+)ml", t)
        if m2:
            val = int(m2.group(1))
            logger.debug("Capacidad detectada: %d ml", val)
            return val
    return None


def _detect_oz(text: str, tokens: list[str]) -> Optional[int]:
    m = re.search(r"(\d+)\s*oz", text)
    if m:
        val = int(m.group(1))
        logger.debug("Capacidad detectada: %d oz", val)
        return val
    for t in tokens:
        m2 = re.match(r"(\d+)oz", t)
        if m2:
            val = int(m2.group(1))
            logger.debug("Capacidad detectada: %d oz", val)
            return val
    return None


def _detect_litros(text: str, tokens: list[str]) -> Optional[float]:
    m = re.search(r"(\d+[.]?\d*)\s*(litro|l)", text)
    if m:
        val = float(m.group(1))
        logger.debug("Capacidad detectada: %.1f litros", val)
        return val
    for t in tokens:
        m2 = re.match(r"(\d+[.]?\d*)l$", t)
        if m2:
            val = float(m2.group(1))
            logger.debug("Capacidad detectada: %.1f litros", val)
            return val
    return None


def _detect_mah(text: str, tokens: list[str]) -> Optional[int]:
    m = re.search(r"(\d+)\s*mah", text)
    if m:
        val = int(m.group(1))
        logger.debug("Capacidad detectada: %d mah", val)
        return val
    for t in tokens:
        m2 = re.match(r"(\d+)mah", t)
        if m2:
            val = int(m2.group(1))
            logger.debug("Capacidad detectada: %d mah", val)
            return val
    return None


def is_known(token: str) -> bool:
    return bool(re.match(r"\d+ml|\d+oz|\d+mah|\d+l$", token))
