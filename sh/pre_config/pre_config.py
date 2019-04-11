import argparse
import yaml
import dicttoxml
from xml.dom.minidom import parseString


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--site_config', help="Compiled Site Level Configuration YAML file")
    parser.add_argument('--execution_id', help="ID of lightweight component")
    parser.add_argument('--output_dir', help="Output directory")
    args = parser.parse_args()
    return {
        'augmented_site_level_config_file': args.site_config,
        'execution_id': args.execution_id,
        'output_dir': args.output_dir
    }


def get_current_lightweight_component(data, execution_id):
    current_lightweight_component = None
    for lightweight_component in data['lightweight_components']:
        if lightweight_component['execution_id'] == int(execution_id):
            current_lightweight_component = lightweight_component
            break
    return current_lightweight_component


def generate_xml(properties, root="configuration", xml_headers=None):
    if xml_headers is None:
        xml_headers = [
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
            "<?xml-stylesheet type=\"text/xsl\" href=\"configuration.xsl\"?>"
        ]
    xml_headers_string = '\n'.join(xml_headers)
    xml_content = []
    for property in properties:
        xml_content.append({
            "property": property
        })
    xml_string = parseString(dicttoxml.dicttoxml(xml_content,
                                                 custom_root=root,
                                                 attr_type=False,
                                                 item_func=lambda x: None).replace('<None>', '').replace('</None>', '')).toprettyxml()
    xml_content = xml_string.split('\n')
    xml_string = '\n'.join(xml_content[1:])
    output = "{xml_headers_string}\n{xml_string}".format(xml_headers_string=xml_headers_string, xml_string=xml_string)
    return output


def get_core_site_xml_content(data, execution_id):
    current_lightweight_component = get_current_lightweight_component(data, execution_id)
    config = current_lightweight_component['config']
    xml_headers = ["<?xml-stylesheet type=\"text/xsl\" href=\"configuration.xsl\"?>"]
    root = "configuration"
    properties = []

    fs_default_name_property = {
            "name": "fs.default.name",
            "value": "hdfs://{fs_default_name}:9000".format(fs_default_name=config['fs_default_name'])
        }
    properties.append(fs_default_name_property)
    output = generate_xml(properties)
    return output


def get_hdfs_site_xml_content(data, execution_id):
    current_lightweight_component = get_current_lightweight_component(data, execution_id)
    config = current_lightweight_component['config']
    xml_headers = ["<?xml-stylesheet type=\"text/xsl\" href=\"configuration.xsl\"?>"]
    root = "configuration"
    properties = []

    dfs_namenode_name_dir_property = {
        "name": "dfs.namenode.name.dir",
        "value": "/root/data/nameNode"
    }

    dfs_datanode_data_dir = {
        "name": "dfs.datanode.data.dir",
        "value": "/root/data/dataNode"
    }

    dfs_replication_property = {
        "name": "dfs.replication",
        "value": config['hdfs_dfs_replication']
    }
    properties.extend([dfs_datanode_data_dir, dfs_namenode_name_dir_property, dfs_replication_property])
    output = generate_xml(properties)
    return output


def get_mapred_site_xml_content(data, execution_id):
    current_lightweight_component = get_current_lightweight_component(data, execution_id)
    config = current_lightweight_component['config']
    xml_headers = ["<?xml-stylesheet type=\"text/xsl\" href=\"configuration.xsl\"?>"]
    root= "configuration"
    properties = []

    mapreduce_framework_name = {
        "name": "mapreduce.framework.name",
        "value": "yarn"
    }

    yarn_app_mapreduce_am_resource_mb = {
        "name": "yarn.app.mapreduce.am.resource.mb",
        "value": config['yarn_app_mapreduce_am_resource_mb']
    }

    mapreduce_map_memory_mb = {
        "name": "mapreduce.map.memory.mb",
        "value": config['mapreduce_map_memory_mb']
    }

    mapreduce_reduce_memory_mb = {
        "name": "mapreduce.reduce.memory.mb",
        "value": config["mapreduce_reduce_memory_mb"]
    }
    properties.extend([mapreduce_framework_name, yarn_app_mapreduce_am_resource_mb, mapreduce_map_memory_mb, mapreduce_reduce_memory_mb])
    output = generate_xml(properties, root, xml_headers)
    return output


if __name__ == "__main__":
    args = parse_args()
    execution_id = args['execution_id']
    site_config_filename =  args['augmented_site_level_config_file']
    site_config = open(site_config_filename, 'r')
    data = yaml.load(site_config)
    output_dir = args['output_dir']
    with open("{output_dir}/core-site.xml".format(output_dir=output_dir), 'w') as core_site:
        core_site.write(get_core_site_xml_content(data, execution_id))

    with open("{output_dir}/hdfs-site.xml".format(output_dir=output_dir), 'w') as core_site:
        core_site.write(get_hdfs_site_xml_content(data, execution_id))

    with open("{output_dir}/mapred-site.xml".format(output_dir=output_dir), 'w') as core_site:
        core_site.write(get_mapred_site_xml_content(data, execution_id))
