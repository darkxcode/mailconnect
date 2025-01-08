import os
from django.core.management.utils import get_random_secret_key

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the .env file
env_file_path = os.path.join(current_dir, '.env')

# Generate a new secret key
new_secret_key = get_random_secret_key()

# Read the current contents of the .env file
with open(env_file_path, 'r') as file:
    env_contents = file.readlines()

# Update the DJANGO_SECRET_KEY line
for i, line in enumerate(env_contents):
    if line.startswith('DJANGO_SECRET_KEY='):
        env_contents[i] = f'DJANGO_SECRET_KEY={new_secret_key}\n'
        break
else:
    # If DJANGO_SECRET_KEY line doesn't exist, add it
    env_contents.append(f'DJANGO_SECRET_KEY={new_secret_key}\n')

# Write the updated contents back to the .env file
with open(env_file_path, 'w') as file:
    file.writelines(env_contents)

print("Secret key has been generated and added to the .env file.")