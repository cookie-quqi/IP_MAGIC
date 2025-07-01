import ipaddress
from ip_converter import mask_to_cidr, cidr_to_mask


def calculate_vlsm(base_ip, subnet_spec):
    "计算VLSM子网划分"
    try:
        # 解析基础网络
        if '/' in base_ip:
            base_network = ipaddress.ip_network(base_ip, strict=False)
        elif ' ' in base_ip:
            ip_part, mask_part = base_ip.split()
            cidr = mask_to_cidr(mask_part)
            base_network = ipaddress.ip_network(f"{ip_part}/{cidr}", strict=False)
        else:
            # 默认使用/32
            base_network = ipaddress.ip_network(f"{base_ip}/32", strict=False)

        # 解析子网掩码规格
        target_cidr = mask_to_cidr(subnet_spec)
        target_mask = cidr_to_mask(target_cidr)

        # 计算子网数量
        base_cidr = base_network.prefixlen
        subnet_count = 2 ** (target_cidr - base_cidr)

        # 生成所有子网
        subnets = []
        current_network = base_network
        for i in range(subnet_count):
            # 计算子网信息
            network_addr = current_network.network_address
            broadcast_addr = current_network.broadcast_address
            host_min = network_addr + 1
            host_max = broadcast_addr - 1
            host_count = current_network.num_addresses - 2
            
            if host_count < 0:
                host_range = "无可用主机"
            elif host_count == 0:
                host_range = f"{host_min}"  # 只有一个地址
            else:
                host_range = f"{host_min} - {host_max} ({host_count}台主机)"

            subnets.append({
                'network': str(network_addr),
                'broadcast': str(broadcast_addr),
                'mask': target_mask,
                'host_range': host_range
            })

            # 计算下一个子网
            current_network = ipaddress.ip_network(f"{broadcast_addr + 1}/{target_cidr}", strict=False)

        return subnets
    except Exception as e:
        raise ValueError(f"VLSM计算错误: {str(e)}")