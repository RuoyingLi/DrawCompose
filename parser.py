import json
import docker
import logging


def extract_objects(jsonFile):
    with open(jsonFile) as json_file:
        data = json.load(json_file)
    things = {'shapes':[],'texts':[]}
    for i in range(len(data['recognitionUnits'])):
        obj = data['recognitionUnits'][i]
        if obj['category'] == 'inkDrawing':
            curr_obj = recShape(obj['center'],obj['recognizedObject'],
                                obj['alternates'])
            things['shapes'].append(curr_obj)
        elif obj['category'] == 'inkWord':
            curr_obj = recText(obj['boundingRectangle'],obj['recognizedText'],
                                obj['alternates'])
            things['texts'].append(curr_obj)
    return things
    

def get_mode(things):
    switcher={
        "isoscelesTriangle": "docker",
        "square": "docker",
        "rightTriangle" : "docker",
        "equilateralTriangle": "docker"
    }
    return switcher.get(things['shapes'][0].object,"docker")

# def collect(jsonFiles):
#     all_components = []
#     for i in jsonFiles:
#         obj = extract_objects(i)
#         obj = check_type(obj)
#         all_components.append(obj)
#     return all_components


class recText():
    def __init__ (self, boundingRectangle, recognizedText, alternates):
        """
        boundingRectangle: dict{'height', 'topX', 'topY', 'width'}
        """
        self.boundingRectangle = boundingRectangle
        self.text = recognizedText
        self.alternates = []
        for i in alternates:
            self.alternates.append(i['recognizedString'])
        
class recShape():
    def __init__ (self, center, recognizedObject, alternates):
        """
        center: dict{'x','y}
        """
        self.center = center
        self.object = recognizedObject
        self.alternates = []
        for i in alternates:
            self.alternates.append(i['recognizedString'])

def create_yaml():
    ymlFile = 'version: "3.7"\nservices:\n'
    f = open('docker-compose.yml','w')
    f.write(ymlFile)
    f.close()
    return True

def update_yaml(service):
    f = open('docker-compose.yml','a')
    strings = '  %s:\n    image: %s\n'%(service['service'],service['image'])
    f.write(strings)
    f.close()
    return True


# all_components = collect(['one_docker.json','one_docker.json'])

# write_yaml(all_components)






def get_docker_service_and_image(lines):
    logging.debug("Extracting service name and image name from lines..")
    client = docker.from_env()
    
       
    service_name = lines[0].text
    image_object = lines[1]
    for search_string in ([image_object.text] + image_object.alternates):
        search_results = client.images.search(search_string)
        if search_results != []:
            break

    image_name = search_results[0]['name']

    return {'service' : service_name, 'image' : image_name}
    
    
def interpret(jsonDoc):
    logging.debug("Extracting text lines from json...")
    objs = extract_objects('one_docker.json')
    logging.debug("Done.")
    if get_mode(objs) == "docker":
        lines = objs['texts']
        service = get_docker_service_and_image(lines)
        update_yaml(service)

if __name__ == "__main__":
    interpret('one_docker.json')