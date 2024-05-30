import json
import requests
import urllib
import boto3
from datetime import datetime
import global_settngs

POST_URL:str = "https://www.printpac.co.jp/contents/lineup/seal/ajax/get_price.php"

# 商品ID
PRODUCT_PRM_NAME = "category_id"
PRODUCT_ID = 47

# 形とサイズ - 全て取る or 必要なものを確認する
SHAPE_AND_SIZE_PRM_NAME:str = "size_id"
SHAPE_AND_SIZE:dict = {
    600 : "正方形60x60" ,
    601 : "正方形50x50" ,
}

# 印刷用紙 - 全て取る or 必要なものを確認する
PRINT_PAPER_PRM_NAME:str="paper_arr[]"
PRINT_PAPAER:dict = {
    159: "クラフト",
    154: "ミラーコート",
}

# 加工 - 多分パターンがないのですべて取ることになる
PROCESS_PRM_NAME:str="kakou"
PROCESS:dict = {
    1 : "印刷のみ",
    2 : "光沢グロスラミネート",
}

# 税込表記 - どちらが良いか確認する
TAX_PRM_NAME:str = "tax_flag"
TAX_PRM_VALUE:str = "true"

#TODO: 組み合わせによっては色ありの場合もあるので、その場合はどうするか検討する

def doCrawl()->bool:
    """
        この関数I/Fを必ず実装してください。
            ⚫︎ 対象データを取得してS3に放り込むところまでを実装
            ⚫︎ 相対する同時作成するBigQueryの登録プログラムが利用しやすい形式であれば、データ形式は自由
            ⚫︎ 成否をBooleanで返却する。必要なログ出力を行うこと
    """
    output_data:dict = get_price()
    put_s3(output_data)
    return True;


def get_price() -> dict:
    # NOTE: 基本的には総当たりで出力して取れないものは存在しない組み合わせとしてSKIPした方が良さそう
    post_data = {}
    for shape_size in SHAPE_AND_SIZE:
        for paper in PRINT_PAPAER:
            for process in PROCESS:
                post_data = {
                    PRODUCT_PRM_NAME: PRODUCT_ID,
                    SHAPE_AND_SIZE_PRM_NAME: shape_size,
                    PRINT_PAPER_PRM_NAME: paper,
                    PROCESS_PRM_NAME: process,
                    TAX_PRM_NAME: TAX_PRM_VALUE
                }
                
                # POST
                post_data = urllib.parse.urlencode(post_data)
                r = requests.post(
                    POST_URL, 
                    data=post_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"})
                    
                if r.status_code != 200:
                    #FIXME: 存在しない組み合わせがあるのでここはうまく回避した方が良い
                    raise Exception("Error at post. Status Code is " + str(r.status_code))
                    
                res_data = r.json()["tbody"]["body"]
                
                for unit in res_data:
                    for eigyo in res_data[unit]:
                        res_data[unit][eigyo]["SHAPE"] = SHAPE_AND_SIZE[shape_size]  
                        res_data[unit][eigyo]["PRINT"] = PRINT_PAPAER[paper]  
                        res_data[unit][eigyo]["KAKOU"] = PROCESS[process]  
                        res_data[unit][eigyo]["UNIT"] = unit
                        res_data[unit][eigyo]["eigyo"] = eigyo
    
    return res_data


def put_s3(output_data:dict):
    """
        buket名とパスのルートのみ共通定数を利用してください
            バケット名： global_settngs.S3_PRICING_BUCKET_NAME
            ルートパス： global_settngs.S3_PRICING_SUBDIR_PATH
            ファイル名： 任意（相対して同時作成するBigQueryの登録プログラムで識別できるようにしてください）
    """
    s3 = boto3.client('s3')
    bucket = global_settngs.S3_PRICING_BUCKET_NAME
    key = global_settngs.S3_PRICING_SUBDIR_PATH  + "printpack-seal-teikei_" + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.json'
    res = s3.put_object(Body=json.dumps(output_data, ensure_ascii=False).encode('utf-8'), Bucket=bucket, Key=key)
