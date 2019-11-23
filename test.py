import json

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
        "isoscelesTriangle": dockerObject(things),
        "square": dockerObject(things),
        "rightTriangle" : dockerObject(things),
        "equilateralTriangle": dockerObject(things)
    }
    return switcher.get(things['shapes'][0].object,'Invalid Object')

def collect(jsonFiles):
    all_components = []
    for i in jsonFiles:
        obj = extract_objects(i)
        obj = check_type(obj)
        all_components.append(obj)
    return all_components


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

class dockerObject():
    def __init__(self, things):
        self.service = things['texts'][0].text.lower()
        self.image = things['texts'][1] .text.lower()
        

def write_yaml(all_components):
    ymlFile = 'version: "3.7"\nservices:\n'
    for comp in all_components:
        strings = '  %s:\n    image: %s\n'%(comp.service,comp.image)
        ymlFile+=strings
    f = open('write_test.yml','w')
    f.write(ymlFile)
    f.close()


all_components = collect(['one_docker.json','one_docker.json'])

write_yaml(all_components)



