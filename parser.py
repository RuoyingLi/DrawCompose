import json
import docker


def extract_objects(json_str):
    data = json.loads(json_str)
    things = {'shapes':[],'texts':[]}
    for i in range(len(data['recognitionUnits'])):
        obj = data['recognitionUnits'][i]
        if obj['category'] == 'inkDrawing':
#             curr_obj = recShape(obj['center'],obj['recognizedObject'],
#                                 obj['alternates'])
            curr_obj = recShape(obj['recognizedObject'])
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
        "rectangle" : "docker",
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
#     def __init__ (self, center, recognizedObject, alternates):
    def __init__ (self, recognizedObject):
        """
        center: dict{'x','y}
        """
#         self.center = center
        self.object = recognizedObject
#         self.alternates = []
#         for i in alternates:
#             self.alternates.append(i['recognizedString'])

def create_yaml():
    ymlFile = 'version: "3.7"\nservices:\n'
    f = open('docker-compose.yml','w')
    f.write(ymlFile)
    f.close()
    return True

def update_service(service):
    f = open('.current_service','w')
    strings = '  %s:\n    image: %s\n'%(service['service'],service['image'])
    f.write(strings)
    f.close()
    return True

def dismiss_current_service():
    f = open('.current_service','w')
    f.close()
    return True

def update_yaml():
    s = open('.current_service','r')
    ls = s.readlines()
    s.close()
    f = open('docker-compose.yml', 'a')
    f.writelines(ls)
    f.close()
    return True

# all_components = collect(['one_docker.json','one_docker.json'])

# write_yaml(all_components)






def get_docker_service_and_image(lines):
    client = docker.from_env()
    
       
    service_name = lines[0].text
    image_object = lines[1]
    for search_string in ([image_object.text] + image_object.alternates):
        search_results = client.images.search(search_string)
        if search_results != []:
            break

    image_name = search_results[0]['name']

    return {'service' : service_name.lower(), 'image' : image_name}

def delete_last_two_lines():
    file = open("docker-compose.yml")
    lines = file.readlines()
    lines = lines[:-2]
    file.writelines(lines)
    return True
    
def interpret(jsonstr):
    objs = extract_objects(jsonstr)
    if get_mode(objs) == "docker":
        lines = objs['texts']
        service = get_docker_service_and_image(lines)
        update_service(service)

if __name__ == "__main__":
    create_yaml()
    interpret(open('one_docker.json', 'r').read())
    update_yaml()
