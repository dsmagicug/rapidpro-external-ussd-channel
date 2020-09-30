# from websocket import create_connection
# import json
#
# ws = create_connection("ws://localhost:8000/ws/demo")
# print("Sending 'Hello, World'...")
#
# payload = {
#     "message": "start code",
#     "from": "rapidpro",
#     "to": "077363256"
# }
# ws.send(json.dumps(payload))
# ws.close()
# print("message sent")

import re

format_string = "{{text=responseString}}, {{action=signal}}"
request_data = {
    'ussdRequestString': "Wrote you a letter, didn't wanna see you eyes, gonna hold onto my feelings no matter who is wrong or right",
    'msisdn': '077363256',
    'creationTime': '2020-04-23T18:25:43.511Z',
    'transactionId': '67684682684823428378',
    'ussdServiceCode': '255*35'}


def separate_keys(string):
    """'
    @string => a string in the format of "{{short_code=ussdServiceCode}},  {{session_id=transactionId}}"
    """
    rapidpro_keys = []
    handler_keys = []
    matches = re.compile('{{(.*?)}}', re.DOTALL).findall(string)
    for match in matches:
        split_list = match.split("=")
        rapidpro_keys.append(split_list[0].strip())
        handler_keys.append(split_list[1].strip())

    return [rapidpro_keys, handler_keys]


rapidpro_keys, handler_keys = separate_keys(format_string)

# get positions of text and action then get corresponding ones in the other list


# # remove all we never defined in the template
# removed = [request_data.pop(v, None) for v in not_in_template if len(not_in_template) > 0]
#
# for item in map_list:
#     if item is not None:
#         request_data[item[0]] = request_data.pop(item[1])
#
# print(request_data)
