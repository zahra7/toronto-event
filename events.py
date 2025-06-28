import yaml
import xml.etree.ElementTree as xmlTree

with open('events.yaml', 'r') as file:
    yamlData = yaml.safe_load(file);

    rssElement = xmlTree.Element('rss', {'version':'2.0',
        'xmlns:atom':'http://www.w3.org/2005/Atom',
        'xmlns:georss':'http://www.georss.org/georss'});
    channelElement = xmlTree.SubElement(rssElement, 'channel');
    xmlTree.SubElement(channelElement, 'title').text = yamlData['title'];

    outputTree = xmlTree.ElementTree(rssElement);
    outputTree.write('event.xml', encoding='UTF-8', xml_declaration=True);