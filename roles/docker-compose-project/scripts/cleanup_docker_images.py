#!/usr/bin/env python3
import json
import logging
import subprocess as sp


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s, %(message)s')

    containers = sp.check_output(('docker', 'ps', '--all', '--format', 'json', '--no-trunc')).strip().splitlines()
    used_images = set()
    for container_data in (json.loads(x) for x in containers):
        insp_data = json.loads(
            sp.check_output(('docker', 'inspect', '--format', 'json', container_data['ID'])),
        )
        used_images.add(insp_data[0]['Image'])

    images = sp.check_output(('docker', 'images', '--no-trunc', '--format', 'json')).strip().splitlines()
    images_to_remove = set()
    for image_data in (json.loads(x) for x in images):
        if image_data['ID'] not in used_images:
            images_to_remove.add(image_data['ID'])

    if images_to_remove:
        sp.check_call(('docker', 'rmi', '--force', *images_to_remove))
        logging.info('Removed %d images', len(images_to_remove))
    else:
        logging.info('No images to remove')


if __name__ == '__main__':
    main()
