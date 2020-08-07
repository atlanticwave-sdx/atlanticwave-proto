# Usage:
# python GenerateSpanningTree.py -m MANIFEST_FILE
# python GenerateSpanningTree.py -m ../configuration/renci_testbed/renci_ben.manifest

import argparse
import json
import networkx as nx
from threading import Lock
from SteinerTree import make_steiner_tree
from networkx.readwrite import json_graph

def TOPO_VALID_TYPE(typestr):
    if (typestr == "switch" or
        typestr == "localcontroller" or
        typestr == "sdxcontroller" or
        typestr == "host" or
        typestr == "dtn" or
        typestr == "network"):
        return True
    return False

def import_topology(manifest_filename, topo, lcs, topolock, nodes):
    with open(manifest_filename) as data_file:
        data = json.load(data_file)

    for unikey in data['endpoints'].keys():
        print(unikey + '\n')
        nodes.append(unikey)
        # All the other nodes
        key = str(unikey)
        endpoint = data['endpoints'][key]
        #FIXME: Validation?
        with topolock:
            if not topo.has_node(key):
                topo.add_node(key)
            for k in endpoint:
                if k == "type" and not TOPO_VALID_TYPE(endpoint[k]):
                    raise TopologyManagerError("Invalid type string %s" %
                                                endpoint[k])
                elif type(endpoint[k]) == int:
                    topo.node[key][k] = int(endpoint[k])
                    topo.node[key][k] = str(endpoint[k])
            # Add other required fields to the endpoitn dict
            topo.node[key]['vlans_in_use'] = []
                

    for key in data['localcontrollers'].keys():
        # Generic per-location information that applies to all switches at
        # a location.
        entry = data['localcontrollers'][key]
        shortname = str(entry['shortname'])
        location = str(entry['location'])
        lcip = str(entry['lcip'])
        org = str(entry['operatorinfo']['organization'])
        administrator = str(entry['operatorinfo']['administrator'])
        contact = str(entry['operatorinfo']['contact'])
        
        # Add shortname to the list of valid LocalControllers
        lcs.append(shortname)

        # Fill out topology
        with topolock:
            # Add local controller
            topo.add_node(str(key))
            topo.node[key]['type'] = "localcontroller"
            topo.node[key]['shortname'] = shortname
            topo.node[key]['location'] = location
            topo.node[key]['ip'] = lcip
            topo.node[key]['org'] = org
            topo.node[key]['administrator'] = administrator
            topo.node[key]['contact'] = contact
            topo.node[key]['internalconfig'] = entry['internalconfig']

            # Add switches to the local controller. Actually happens after
            # the switches are handled.
            switch_list = []

            # Switches for that LC
            for switchinfo in entry['switchinfo']:
                name = str(switchinfo['name'])
                # Node may be implicitly declared, check this first.
                if not topo.has_node(name):
                    topo.add_node(name)

                # Add switch to LC list. This will be added at the end.
                switch_list.append(name)
                
                # Per switch info, gets added to topo
                topo.node[name]['friendlyname'] = str(switchinfo['friendlyname'])
                topo.node[name]['dpid'] = int(switchinfo['dpid'], 0) #0 guesses base.
                topo.node[name]['ip'] = str(switchinfo['ip'])
                topo.node[name]['brand'] = str(switchinfo['brand'])
                topo.node[name]['model'] = str(switchinfo['model'])
                topo.node[name]['locationshortname'] = shortname
                topo.node[name]['location'] = location
                topo.node[name]['lcip'] = lcip
                topo.node[name]['lcname'] = key
                topo.node[name]['org'] = org
                topo.node[name]['administrator'] = administrator
                topo.node[name]['contact'] = contact
                topo.node[name]['type'] = "switch"

                # Other fields that may be of use
                topo.node[name]['vlans_in_use'] = []

                topo.node[name]['internalconfig'] = switchinfo['internalconfig']

                # Add the links
                for port in switchinfo['portinfo']:
                    portnumber = int(port['portnumber'])
                    speed = int(port['speed'])
                    destination = str(port['destination'])

                    # If link already exists
                    if not topo.has_edge(name, destination):
                        topo.add_edge(name, destination, weight=speed)
                    # Set the port number for the current location. The dest
                    # port should be set when the dest side has been run.
                    topo.edge[name][destination][name] = portnumber

                    # Other fields that may be of use
                    topo.edge[name][destination]['vlans_in_use'] = []
                    topo.edge[name][destination]['bw_in_use'] = 0

                    # VLANs available
                    if 'available_vlans' in port.keys():
                        topo.edge[name][destination]['available_vlans'] = str(port['available_vlans'])
                    elif 'available_vlans' in topo.node[port['destination']].keys():
                        topo.edge[name][destination]['available_vlans'] = str(topo.node[port['destination']]['available_vlans'])
                    else:
                        topo.edge[name][destination]['available_vlans'] = "0-4095"

            # Once all the switches have been looked at, add them to the LC
            topo.node[key]['switches'] = switch_list

def parse_manifest(manifest_filename):
    with open(manifest_filename) as data_file:
        data = json.load(data_file)

    for key in data['localcontrollers']:
        entry = data['localcontrollers'][key]
        shortname = entry['shortname']
        credentials = entry['credentials']
        lcip = entry['lcip']
        switchips = []
        for sw in entry['switchinfo']:
            switchips.append(sw['ip'])
    
    return data

def find_vlan_on_tree(tree, topo):
        ''' Tree version of find_vlan_on_path(). Finds a VLAN that's not being
            used at the moment on a provivded path. Returns an available VLAN if
            possible, None if none are available on the submitted tree. '''
        print("find_vlan_on_tree: %s" % tree.nodes()) 
        selected_vlan = None
        for vlan in range(1,4089):
            # Check each point on the path
            on_path = False
            for node in tree.nodes():
                if 'type' in topo.node[node] and topo.node[node]['type'] == "switch":
                    if vlan in topo.node[node]['vlans_in_use']:
                        on_path = True
                        break
                
            if on_path:
                continue

            # Check each edge on the path
            for (node, nextnode) in tree.edges():
                if vlan in topo.edge[node][nextnode]['vlans_in_use']:
                    on_path = True
                    break
                
            if on_path:
                continue

            # If all good, set selected_vlan
            selected_vlan = vlan
            break

        print("find_vlan_on_tree returning %s" % selected_vlan)
        return selected_vlan

def find_valid_steiner_tree(nodes, topo, bw=None):
    ''' Finds a Steiner tree connecting all the nodes in 'nodes' together. 
        Uses a library containing Kou's algorithm to find one. 
        Returns a graph, from with .nodes() and .edges() can be used
        to call other functions. '''
    
    # Loop through, trying to make a valid Steiner tree that has available
    # bandwidth. This will either return something valid, or will blow up
    # due to a path not existing and will return nothing.
    # timeout is a just-in-case measure
    timeout = len(topo.edges())
    while(timeout > 0):
        timeout -= 1
        
        try:
            tree = make_steiner_tree(topo, nodes)
            print("find_valid_steiner_tree: found %s" % (tree.edges()))

        except ValueError:
            raise
        except nx.exception.NetworkXNoPath:
            #FIXME: log something here.
            return None

        # Check if enough bandwidth is available
        enough_bw = True
        for (node, nextnode) in tree.edges():
            # For each edge on the path, check that bw is available.
            bw_in_use = topo.edge[node][nextnode]['bw_in_use']
            bw_available = int(topo.edge[node][nextnode]['weight'])

            if bw is not None and (bw_in_use + bw) > bw_available:
                enough_bw = False
                # Remove the edge that doesn't have enough bw and try again
                topo.remove_edge(node, nextnode)
                break
        if not enough_bw:
            continue
            

        # Check if VLAN is available
        selected_vlan = find_vlan_on_tree(tree, topo)
        if selected_vlan == None:
            #FIXME: how to handle this?
            print("find_valid_steiner_tree: Could not find VLAN, unhandled!")
            pass

        # Has BW and VLAN available, return it.
        #print("find_valid_steiner_tree: Successful %s" %
        #                    tree.edges())

        print("Json steiner tree:")
        #json_data = json.dumps(dict(nodes=tree.nodes(), edges=tree.edges()))

        data = {}

        for node in tree.nodes():
            for edge in tree.edges():
                if  node in edge:
                    if node in data:
                        if (edge[0] == node):
                            data[node].append(edge[1])
                        else:
                            data[node].append(edge[0])
                    else:
                        data[node] = []
                        if (edge[0] == node):
                            data[node].append(edge[1])
                        else:
                            data[node].append(edge[0])
                        #data[node].append(edge)
        
        print(json.dumps(data))
        json_data = json.dumps(data)

        tree_file_name = append_name(mani, 'spanning_tree')
        with open(tree_file_name, 'w') as out:
            out.write(json_data)
        out.close()
        
        return tree

def append_name(filename, appendix):
    return "{0}_{2}.{1}".format(*filename.rsplit('.', 1) + [appendix])

if __name__ == '__main__':
    #from optparse import OptionParser
    #parser = OptionParser()

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-d", "--database", dest="database", type=str, 
                        action="store", help="Specifies the database ", 
                        default=":memory:")

    parser.add_argument("-m", "--manifest", dest="manifest", type=str, 
                        action="store", help="specifies the manifest")    

    options = parser.parse_args()

    if not options.manifest:
        parser.print_help()
        exit()

    mani = options.manifest
    results = parse_manifest(mani)

    topo = nx.Graph()
    lcs = []
    topolock = Lock()
    nodes = []
    import_topology(mani, topo, lcs, topolock, nodes)
    find_valid_steiner_tree(nodes, topo)
