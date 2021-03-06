"""

AUTHOR: IPvZero(main), kit_chrisr(modifications)
DATE: 22 Oct 2020

changelog:
2020/10/21 - ipvzero: first code (majority)
2020/10/21 - kit_chrisr: change to show mac address-table
2020/10/22 - kit_chrisr: include descriptions on interfaces


"""

import os
import logging
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from rich import print as rprint
import json
nr = InitNornir(config_file="config.yaml")
break_list = []

CLEAR = "clear"
os.system(CLEAR)
target = input("Enter the mac address you wish to find: ")


def pull_info(task):


    """
    1) If MAC address is present, identify Device and Interface
    """
    
    result = task.run(
        task=netmiko_send_command, command_string="show mac address-table", use_genie=True
    )
    task.host["facts"] = result.result
    mac_addresses = task.host["facts"]["mac_table"]["vlans"]
    for vlan in mac_addresses.keys():
        if vlan != "all":
            for mac_address in mac_addresses[vlan]["mac_addresses"].keys():
                if target == mac_address:
                    break_list.append(target)
                    interface_descr = get_interface_descriptions(task,mac_addresses[vlan]["mac_addresses"][mac_address]["interfaces"])
                    print_info(task,mac_address, vlan, mac_addresses[vlan]["mac_addresses"][mac_address]["interfaces"],interface_descr)


def get_interface_descriptions(task, interfaces):
    descriptions = {}
    iresult = task.run(
        task=netmiko_send_command, command_string="show interfaces", use_genie=True
    )

    # note show interface {interface} would be nicer, but genie has an issue doing this on port-channels
    for interface in interfaces.keys():
        if interface in iresult.result:
            descriptions[interface] = iresult.result[interface]['description']
        else:
            descriptions[interface] = 'n/a'
    return descriptions


def print_info(task, mac_address,vlan,interfaces,descriptions):

    """
    Execute show cdp neighbor and show version commands
    on target device. Parse information and return output
    """
    str_interface = ""
    for interface in interfaces.keys():
        str_interface = str_interface + interface + "(" + descriptions[interface] + "),"
    rprint("\n[green]*** TARGET IDENTIFIED ***[/green]")
    print(f"MAC ADDRESS: {target} is present on {task.host}'s")
    rprint("\n[cyan]GENERATING DETAILS...[/cyan]")
    print(f"{task.host} : {mac_address} : vlan {vlan} : interface(s) - {str_interface}")

results = nr.run(task=pull_info)
if target not in break_list:
    rprint("[red]TARGET NOT FOUND[/red]")
