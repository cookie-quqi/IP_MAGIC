import re

def is_valid_ip(ip):
    "验证IP地址是否有效，支持十进制和二进制格式，带或不带子网掩码"
    # 十进制IP地址格式 (如 192.168.1.1 或 192.168.1.1/24 或 192.168.1.1 255.255.255.0)
    decimal_pattern = r'^(\d{1,3}\.){3}\d{1,3}(\s+(\d{1,3}\.){3}\d{1,3}|/\d{1,2})?$'
    # 二进制IP地址格式 (32位二进制数，可选带子网掩码)
    binary_pattern = r'^([01]{8}\.){3}[01]{8}(\s+([01]{8}\.){3}[01]{8}|/\d{1,2})?$'
    
    return re.match(decimal_pattern, ip) or re.match(binary_pattern, ip)


def ip_to_binary(ip):
    "将IP地址转换为二进制格式"
    # 分离IP和子网掩码
    ip_part = ip.split('/')[0].split()[0]
    
    # 如果已经是二进制，直接返回
    if all(part in '01.' for part in ip_part):
        return ip_part
    
    # 十进制转二进制
    octets = list(map(int, ip_part.split('.')))
    binary_octets = [format(octet, '08b') for octet in octets]
    return '.'.join(binary_octets)


def binary_to_ip(binary_ip):
    "将二进制IP地址转换为十进制格式"
    octets = binary_ip.split('.')
    decimal_octets = [str(int(octet, 2)) for octet in octets]
    return '.'.join(decimal_octets)


def mask_to_cidr(subnet_mask):
    "将子网掩码转换为CIDR表示法"
    if '/' in subnet_mask:
        return int(subnet_mask.split('/')[1])
    
    # 如果是点分十进制掩码
    if '.' in subnet_mask:
        octets = list(map(int, subnet_mask.split('.')))
        binary_mask = ''.join([format(octet, '08b') for octet in octets])
        return binary_mask.count('1')
    
    # 如果是纯数字
    return int(subnet_mask)


def cidr_to_mask(cidr):
    "将CIDR表示法转换为子网掩码"
    cidr = int(cidr)
    if cidr < 0 or cidr > 32:
        raise ValueError("CIDR值必须在0-32之间")
    
    mask = (0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF
    octets = [(mask >> (8*i)) & 0xFF for i in reversed(range(4))]
    return '.'.join(map(str, octets))