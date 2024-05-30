from crawlers import ppac_seal_teikei

COMMAND_PRM_NAME = "TARGET"

"""
    コマンドと実行するCrawlerの対応表
    Crawler追加時はこちらも合わせて行追加する
    lambdaパラメータ名TARGETに渡す名前
    上記パラメータの際に呼び出すCrawler
"""
COMMAND_MAP:dict = {
 "ppac_seal_teikei" : ppac_seal_teikei,   
}

# S3関連
S3_PRICING_BUCKET_NAME = "mbs-for-test"
S3_PRICING_SUBDIR_PATH = "pricing/"
