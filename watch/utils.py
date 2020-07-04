import os.path

def get_resource_path(filename):
    module_path = os.path.dirname(__file__)
    resource_path = os.path.join(module_path, filename)
    return resource_path


