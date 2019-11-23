import json
import docker
import logging


client = docker.from_env()


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
    

def check_type(things):
    switcher={
        "isoscelesTriangle": gitService(),
        "square": dockerService(things),
        "rightTriangle" : blabla(),
        "equilateralTriangle": blabla()
    }
    return switcher.get(things['shapes'],'Invalid Object')

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

class dockerService():
    def __init__(self, things):
        self.service = things['texts'][0]
        self.image = things['texts'][1] 
        self.dockerfile = "docker_compose.yml"
        
    def makeComposefile(self):
        file = open(self.dockerfile, "w") 
        file.write("FROM %s"%(self.image.text)) 
        file.close() 
        
        



logging.debug("Extracting text lines from json...")
lines = extract_objects('one_docker.json')['texts']
logging.debug("Done.")

logging.debug("Extracting service name and image name from lines..")
def get_docker_service_and_image(lines):
    service_name = lines[0].text
    image_object = lines[1]
    for search_string in ([image_object.text] + image_object.alternates):
        search_results = client.images.search(search_string)
        if search_results != []:
            break

    image_name = search_results[0]['name']

    return {'service' : service_name, 'image' : image_name}

logging.debug("Done.")
