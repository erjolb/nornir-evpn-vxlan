#!/usr/bin/env python

import argparse
import logging
from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_configure
from nornir_jinja2.plugins.tasks import template_file
from nornir_utils.plugins.tasks.data import load_yaml
from nornir_utils.plugins.functions import print_result



def set_interface(task, dry_run):
    # loading innterfaces variables
    interface_vars = task.run(
        load_yaml,
        file=f"host_vars/{task.host}/interfaces.yml",
        severity_level=logging.DEBUG,
    )
    # assiging them to the host object
    task.host["interfaces"] = interface_vars.result["interfaces"]

    # generate configuration
    config = task.run(
        template_file,
        name="Render interface configuration",
        template="interface.j2",
        path=f"templates/{task.host.platform}",
        severity_level=logging.DEBUG,
    )

    # deploy configuraton to the device
    task.run(
        napalm_configure,
        name="Deploy interface configuration",
        configuration=config.result,
        replace=False,
        dry_run=dry_run,
    )

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--hosts", nargs="+", help="Target host")
    p.add_argument("--check", action="store_true", help="Enable check mode")

    args = p.parse_args()

    nr = InitNornir(config_file="nr-config.yml")

    for host in args.hosts:
        target_host = nr.filter(name=host)
        result = target_host.run(task=set_interface, dry_run=args.check)
        print_result(result)


if __name__ == "__main__":
    main()
