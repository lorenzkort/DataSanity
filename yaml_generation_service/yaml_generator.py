import yaml

def generate_yaml(data):
    with open('output.yaml', 'w') as file:
        yaml.dump(data, file)

# Sample data from Claude API
data = {"dashboard": {"name": "Sales Dashboard", "charts": ["bar", "line"]}}
generate_yaml(data)
