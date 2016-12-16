# Copyright (c) 2016 Mirantis, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os

from kuryr_kubernetes.cni.binding import base as b_base


class BridgeDriver(object):
    def connect(self, vif, ifname, netns):
        host_ifname = vif.vif_name
        bridge_name = vif.bridge_name

        c_ipdb = b_base.get_ipdb(netns)
        h_ipdb = b_base.get_ipdb()

        with c_ipdb.create(ifname=ifname, peer=host_ifname,
                           kind='veth') as c_iface:
            c_iface.mtu = vif.network.mtu
            c_iface.address = str(vif.address)
            c_iface.up()

        if netns:
            with c_ipdb.interfaces[host_ifname] as h_iface:
                h_iface.net_ns_pid = os.getpid()

        with h_ipdb.interfaces[host_ifname] as h_iface:
            h_iface.mtu = vif.network.mtu
            h_iface.up()

        with h_ipdb.interfaces[bridge_name] as h_br:
            h_br.add_port(host_ifname)

    def disconnect(self, vif, ifname, netns):
        # NOTE(ivc): veth pair is destroyed automatically along with the
        # container namespace
        pass