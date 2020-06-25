# Usage:
# python GenerateSpanningTree.py -m MANIFEST_FILE
# python GenerateSpanningTree.py -m ../configuration/renci_testbed/renci_ben.manifest

import argparse
import json
import networkx as nx
from threading import Lock
from SteinerTree import make_steiner_tree
from networkx.readwrite import json_graph
from networkx.algorithms import approximation as ax

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
                    topo.nodes[key][k] = int(endpoint[k])
                    topo.nodes[key][k] = str(endpoint[k])
            # Add other required fields to the endpoitn dict
            topo.nodes[key]['vlans_in_use'] = []
                

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
            topo.nodes[key]['type'] = "localcontroller"
            topo.nodes[key]['shortname'] = shortname
            topo.nodes[key]['location'] = location
            topo.nodes[key]['ip'] = lcip
            topo.nodes[key]['org'] = org
            topo.nodes[key]['administrator'] = administrator
            topo.nodes[key]['contact'] = contact
            topo.nodes[key]['internalconfig'] = entry['internalconfig']

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
                topo.nodes[name]['friendlyname'] = str(switchinfo['friendlyname'])
                topo.nodes[name]['dpid'] = int(switchinfo['dpid'], 0) #0 guesses base.
                topo.nodes[name]['ip'] = str(switchinfo['ip'])
                topo.nodes[name]['brand'] = str(switchinfo['brand'])
                topo.nodes[name]['model'] = str(switchinfo['model'])
                topo.nodes[name]['locationshortname'] = shortname
                topo.nodes[name]['location'] = location
                topo.nodes[name]['lcip'] = lcip
                topo.nodes[name]['lcname'] = key
                topo.nodes[name]['org'] = org
                topo.nodes[name]['administrator'] = administrator
                topo.nodes[name]['contact'] = contact
                topo.nodes[name]['type'] = "switch"

                # Other fields that may be of use
                topo.nodes[name]['vlans_in_use'] = []

                topo.nodes[name]['internalconfig'] = switchinfo['internalconfig']

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
                    topo.edges[name][destination][name] = portnumber

                    # Other fields that may be of use
                    topo.edges[name][destination]['vlans_in_use'] = []
                    topo.edges[name][destination]['bw_in_use'] = 0

                    # VLANs available
                    if 'available_vlans' in port.keys():
                        topo.edges[name][destination]['available_vlans'] = str(port['available_vlans'])
                    elif 'available_vlans' in topo.nodes[port['destination']].keys():
                        topo.edges[name][destination]['available_vlans'] = str(topo.nodes[port['destination']]['available_vlans'])
                    else:
                        topo.edges[name][destination]['available_vlans'] = "0-4095"

            # Once all the switches have been looked at, add them to the LC
            topo.nodes[key]['switches'] = switch_list

def export_topology(manifest_filename, topo, lcs, topolock, nodes):
    return

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
                print("node:")
                print(node)
                print("topo.nodes[node]")
                print(topo.nodes[node])
                if 'type' in topo.nodes[node]:
                    print("topo.nodes[node]['type']")
                    print(topo.nodes[node]['type'])
                if 'type' in topo.nodes[node] and topo.nodes[node]['type'] == "switch":
                    if vlan in topo.nodes[node]['vlans_in_use']:
                        on_path = True
                        break
                
            if on_path:
                continue

            # Check each edge on the path
            for (node, nextnode) in tree.edges():
                if vlan in topo.edges[node][nextnode]['vlans_in_use']:
                    on_path = True
                    break
                
            if on_path:
                continue

            # If all good, set selected_vlan
            selected_vlan = vlan
            break

        print("find_vlan_on_tree returning %s" % selected_vlan)
        return selected_vlan

def find_valid_steiner_tree(mani, nodes, topo, bw=None):
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
            graph2 = ax.steinertree.steiner_tree(topo, nodes, weight = 'weight') 
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
            bw_in_use = topo.edges[node][nextnode]['bw_in_use']
            bw_available = int(topo.edges[node][nextnode]['weight'])

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

        edge_list = tree.edges()
        # Has BW and VLAN available, return it.
        print("find_valid_steiner_tree: Successful %s" %
                            tree.edges())
        
#        print(json_graph.node_link_data(tree))
        #print(json.dumps(dict(nodes = tree.nodes(), edges = tree.edges())))
        print(tree.edges())

        tree_file_name = mani + '_spanning_tree'
        with open(tree_file_name, 'a') as out:
            out.write(str(tree.edges()))
        return tree
    
    

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
    find_valid_steiner_tree(mani, nodes, topo)