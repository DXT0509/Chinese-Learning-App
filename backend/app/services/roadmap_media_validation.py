"""Small bounded Ogg/Vorbis container checks; linguistic and audible review stays human."""

import struct


def inspect_vorbis(data: bytes):
    position, expected_sequence, serial = 0, 0, None
    identification, sample_count, ended = None, 0, False
    while position < len(data):
        if ended or data[position : position + 5] != b"OggS\0" or len(data) - position < 27:
            raise ValueError("invalid/truncated Ogg page")
        header = data[position : position + 27]
        segments = header[26]
        lacing = data[position + 27 : position + 27 + segments]
        size = 27 + segments + sum(lacing)
        page = bytearray(data[position : position + size])
        if len(lacing) != segments or len(page) != size:
            raise ValueError("truncated Ogg packet")
        actual_serial, sequence, declared_crc = struct.unpack_from("<III", page, 14)
        if sequence != expected_sequence or (serial is not None and actual_serial != serial):
            raise ValueError("unsupported chained or reordered Ogg stream")
        if sequence == 0 and not header[5] & 2:
            raise ValueError("Ogg stream lacks beginning marker")
        page[22:26] = b"\0" * 4
        crc = 0
        for byte in page:
            crc ^= byte << 24
            for _ in range(8):
                crc = ((crc << 1) ^ (0x04C11DB7 if crc & 0x80000000 else 0)) & 0xFFFFFFFF
        if crc != declared_crc:
            raise ValueError("Ogg page CRC mismatch")
        if sequence == 0:
            packet = data[position + 27 + segments : position + size]
            if len(packet) < 30 or packet[:7] != b"\x01vorbis":
                raise ValueError("expected a Vorbis identification packet")
            version, channels, rate = struct.unpack_from("<IBI", packet, 7)
            if version != 0 or channels not in (1, 2) or not 8000 <= rate <= 96000:
                raise ValueError("unsupported Vorbis identification")
            identification = {"channels": channels, "sample_rate": rate}
        granule = struct.unpack_from("<Q", header, 6)[0]
        if granule != 0xFFFFFFFFFFFFFFFF:
            sample_count = max(sample_count, granule)
        ended = bool(header[5] & 4)
        serial, expected_sequence = actual_serial, expected_sequence + 1
        position += size
    if not ended or not identification or sample_count <= 0:
        raise ValueError("Vorbis stream is incomplete or empty")
    return {
        **identification,
        "duration_ms": round(sample_count * 1000 / identification["sample_rate"]),
        "pages": expected_sequence,
        "crc_verified": True,
    }
