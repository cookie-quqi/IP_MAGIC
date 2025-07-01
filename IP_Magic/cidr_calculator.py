import ipaddress
from ip_converter import mask_to_cidr, cidr_to_mask


def calculate_cidr(ip):
    "计算CIDR并输出多个分支结果"
    try:
        # 解析IP地址和子网掩码
        if '/' in ip:
            network = ipaddress.ip_network(ip, strict=False)
            cidr = network.prefixlen
        elif ' ' in ip:
            ip_part, mask_part = ip.split()
            cidr = mask_to_cidr(mask_part)
            network = ipaddress.ip_network(f"{ip_part}/{cidr}", strict=False)
        else:
            # 默认使用/32
            network = ipaddress.ip_network(f"{ip}/32", strict=False)
            cidr = 32

        results = []
        # 计算CIDR-1, CIDR-2, CIDR-3的结果
        for i in range(1, 4):
            new_cidr = cidr - i
            if new_cidr < 0:
                break
            new_mask = cidr_to_mask(new_cidr)
            new_network = ipaddress.ip_network(f"{network.network_address}/{new_cidr}", strict=False)
            results.append(f"/ {new_cidr} (子网掩码: {new_mask}):")
            results.append(f"  网络地址: {new_network.network_address}")
            results.append(f"  广播地址: {new_network.broadcast_address}")
            results.append(f"  子网范围: {new_network.network_address} - {new_network.broadcast_address}")
            results.append(f"  可用主机数: {new_network.num_addresses - 2}\n")

        return '\n'.join(results)
    except Exception as e:
        return f"CIDR计算错误: {str(e)}"