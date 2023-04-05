import hashlib
import json
import logging

import paho.mqtt.client as mqtt

def segments(data, segment_size):
    offset = 0
    while offset < len(data):
        yield (offset, data[offset:offset + segment_size])
        offset += segment_size

def transfer(client_id, file_id, file_name, **kwargs):
    data = open(file_name, "rb").read()

    hash = hashlib.new('sha256')
    hash.update(data)
    checksum = hash.hexdigest()

    name = kwargs.get('file_name', file_name)
    meta = {
        "name": name,
        "size": len(data),
        "checksum": checksum
    }

    topic_prefix = f"$file/{file_id}"

    client = mqtt.Client(client_id=client_id)
    client.protocol_version = mqtt.MQTTv5

    client.enable_logger(logging.getLogger())
    level = logging.getLogger().getEffectiveLevel()
    logging.getLogger().setLevel(logging.DEBUG)

    client.connect(kwargs.get('host', 'localhost'), kwargs.get('port', 1883), 60)
    client.publish(f"{topic_prefix}/init", json.dumps(meta), qos=1)
    for offset, chunk in segments(data, kwargs.get('segment_size', 1024)):
        client.publish(f"{topic_prefix}/{offset}", chunk, qos=1)
    info = client.publish(f"{topic_prefix}/fin/{len(data)}", "", qos=1)

    def on_publish(client, userdata, mid):
        if mid == info.mid:
            client.disconnect()

    client.on_publish = on_publish

    client.loop_forever()

    logging.getLogger().setLevel(level)
