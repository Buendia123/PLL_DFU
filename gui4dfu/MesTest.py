import json

import requests


# "operationId"": ""3fa85f64-5717-4562-b3fc-2c963f66afa6"
# "operationUserSN"": ""V005885"
# ""lotNo"": ""P10***"",
# host = r'http://172.16.26.86/v5mesapi//openapi/mes/tracking/check'


def MesPostData(operationId, sn, userid, result):
    return True
    try:
        str_msg = ""
        obj = {
            "oeprationId": operationId,
            "lotNo": sn,
            "operationUserSN": userid,
            "result": result
        }
        post_data = json.dump(obj)
        url = f"{host}"
        headers = {"Cotent-Type": "application/json"}
        response = requests.post(url, data=post_data, headers=headers)
        print(response.content)
        cr = json.loads(response.content)
        if cr['code'] == 0:
            return True
        else:
            str_msg = cr["message"]
            return False
    except Exception as ex:
        return False


def MesCheckSN(operationId, sn, userid, host):
    return True
    try:
        str_msg = ""
        obj = {
            "oeprationId": operationId,
            "lotNo": sn,
            "operationUserSN": userid,

        }
        post_data = json.dumps(obj)
        url = f"{host}"
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, data=post_data, headers=headers, timeout=2)
        print(response.content)
        cr = json.loads(response.content)
        if cr['code'] == 0:
            return True
        else:
            str_msg = cr["message"]
            return False
    except Exception as ex:
        return False


def MesPostResult(operationId, sn, userid, result, host):
    return True
    try:
        str_msg = ""
        obj = {
            "oeprationId": operationId,
            "lotNo": sn,
            "operationUserSN": userid,
            "result": result

        }
        post_data = json.dumps(obj)
        url = f"{host}"
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, data=post_data, headers=headers, timeout=2)
        print(response.content)
        cr = json.loads(response.content)
        if cr['code'] == 0:
            return True
        else:
            str_msg = cr["message"]
            return False
    except Exception as ex:
        return False
# operationId=r'3fa85f64-5717-4562-b3fc-2c963f66afa6'
# sn = 'P10***'
# userid = 'V005885'
# MesCheckSN(operationId,sn,userid)
# sn = 'P0232**334'
# result = 'PASS'
# MesPostResult(operationId,sn,userid,result)
# sn = 'x213456-t1'
# MesPostResult(DB.DbProvider.Mes.operationId,sn.split('_')[0],DB.DbProvider.Mes.userid,"PASS",DB.DbProvider.Mes.host_postresult)
