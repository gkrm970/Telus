# Script that will generate new tag values
# It will automatically increment the last version digit master-0.0.x

import os
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=4)
commit = None
prefix = 'master-'
new_tag = None
latest_master_tag = ''


if 'CI_COMMIT_SHA' in os.environ:
    commit = os.getenv('CI_COMMIT_SHA')
else :
    commit = os.popen('git rev-parse HEAD').read().strip('\n')
print(f'Current commit: {commit}')

# Create a dictionary of all existing production tags with their corresponding commits
tags = dict()
tag_list = list()
all_tags = os.popen('git show-ref --tags').read().strip('\n').splitlines()
for row in all_tags:
    sha = row.split()[0]
    tag = row.split()[1].split('/')[2]
    if tag.startswith(prefix):
        tags[tag] = sha
        tag_list.append(tag)

print("Existing production tags:")
if tags:
    pp.pprint(tags)
else:
    print('   No tag found...')
print('')

# Get the latest master-* tag
# Using git describe was unpredictable. The latest version was not always returned for some obscure reason ;-)
# Command kept here for reference only
# latest_master_tag = os.popen('git describe --abbrev=0 --tags --match master-* 2>/dev/null').read().strip('\n')
tag_list.sort(reverse=True)
if tag_list:
    latest_master_tag = tag_list[0]

if latest_master_tag == '':
    # Generate a default master tag if none exist
    new_tag = 'master-0.0.0'
else:
    print(f'Latest tag: {latest_master_tag}')
    
    # Validate that there's no master-* tag on the current commit
    # Throws an error if one exists
    tags_on_commit = list()
    for tag in tags:
        if tags[tag] == commit:
            tags_on_commit.append(tag)
    if tags_on_commit:
        raise Exception(f'Commit {commit} already has production tag: {tags_on_commit}, exiting...')

    # Generate new tag
    current_version = latest_master_tag.lstrip(prefix)
    v1, v2, v3 = current_version.split('.')
    v3 = int(v3) + 1
    new_tag = f"master-{v1}.{v2}.{v3}"

print(f'Creating environment variable file for {new_tag}')
f = open("new_tag.env", "w")
f.write(f"export NEW_TAG={new_tag}\n")
f.close()





