# -*- coding: utf-8 -*-
"""
author: zengbin93
email: zeng_bin8888@163.com
create_dt: 2022/12/16 19:51
describe: 
"""
import os
import pandas as pd
from loguru import logger

logger.enable('fsa.base')


def test_fsa_base():
    from czsc.fsa.base import FeishuApiBase

    app = FeishuApiBase(app_id=os.environ['app_id'], app_secret=os.environ['app_secret'])
    print(app.get_access_token())

    # res = app.upload_file(file_path=r"D:\ZB\git_repo\zengbin93\fsa\fsa\spreed_sheets.py", parent_node='fldcnRHcnV1d1UDs7EWRk1PpcIh')

    # app.copy(token='shtcnLpzhhsKwbmlJXHlrWCp4mf', payload={
    #     "name": "共享文件策略",
    #     "type": "sheet",
    #     "folder_token": "fldcnBD3C3F9ZePfEwdykzIXRtp"
    # })

    # app.move(token='shtcn9fZEefDeGAclDTNc4v6J8e',
    #          payload={"type": "sheet", "folder_token": "fldcnRHcnV1d1UDs7EWRk1PpcIh"})


def test_spread_sheets():
    from czsc.fsa.spreed_sheets import SpreadSheets

    app = SpreadSheets(app_id=os.environ['app_id'], app_secret=os.environ['app_secret'])

    folder_token = app.get_root_folder_token()
    token = app.create(folder_token, title="电子表格API测试")
    token = token['data']['spreadsheet']['spreadsheet_token']
    res = app.get_sheets(token)
    sheet_id = res['data']['sheets'][0]['sheet_id']
    app.delete_values(token, sheet_id)
    meta = app.get_sheet_meta(token, sheet_id)
    assert meta['data']['sheet']['grid_properties']['row_count'] == 1
    assert meta['data']['sheet']['grid_properties']['column_count'] == 1

    df = pd.DataFrame({'x': list(range(100)), 'y': list(range(100)), 'z': list(range(100))})
    app.append(token, sheet_id, df)
    meta = app.get_sheet_meta(token, sheet_id)
    assert meta['data']['sheet']['grid_properties']['row_count'] == 101
    assert meta['data']['sheet']['grid_properties']['column_count'] == 3

    dfr = app.read_table(token, sheet_id)
    assert dfr.shape == df.shape

    app.delete_values(token, sheet_id)
    meta = app.get_sheet_meta(token, sheet_id)
    assert meta['data']['sheet']['grid_properties']['row_count'] == 1
    assert meta['data']['sheet']['grid_properties']['column_count'] == 1

    app.remove(token, kind='sheet')


def test_im():
    from czsc.fsa.im import IM

    app = IM(app_id=os.environ['app_id'], app_secret=os.environ['app_secret'])
    # id = app.get_user_id({"mobiles": ["XXXX"]})['data']['user_list'][0]['user_id']
    receive_id = "ou_6fa04b5b4d853e9fdc87d267e8f2a270"

    image_key = app.upload_im_image(r"C:\Users\zengb\Downloads\十阶众生相.jpg")
    payload = {"receive_id": receive_id, "content": {"image_key": image_key}, "msg_type": "image"}
    print(app.send(payload))

    payload = {"receive_id": receive_id, "content": {"text": "自定义文字随便发"}, "msg_type": "text"}
    print(app.send(payload))

    file_key = app.upload_im_file(r"C:\Users\zengb\Downloads\放量破年线.py")
    payload = {"receive_id": receive_id, "content": {"file_key": file_key}, "msg_type": "file"}
    print(app.send(payload))

    file_key = app.upload_im_file(r"C:\Users\zengb\Downloads\Think Python 2ed 中译版精校.pdf", file_type='pdf')
    payload = {"receive_id": receive_id, "content": {"file_key": file_key}, "msg_type": "file"}
    app.send(payload)

    app.send_text("快捷接口发送自定义文字", receive_id)
    app.send_image(r"C:\Users\zengb\Downloads\十阶众生相.jpg", receive_id)
    app.send_file(r"C:\Users\zengb\Downloads\Think Python 2ed 中译版精校.pdf", receive_id)

