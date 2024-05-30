import json
import global_settngs

def lambda_handler(event, context):
    """
        Crawler追加時にこのファイルを直す必要はありません
    """

    #FIXME: 引数チェックと戻り値チェック    
    print(f"{event["TARGET"]} crawler called.")
    global_settngs.COMMAND_MAP[event[global_settngs.COMMAND_PRM_NAME]].doCrawl()
    
    #FIXME: 適切なbody
    return {
        'statusCode': 200,
        'body': json.dumps(f"{event["TARGET"]} has done.")
    }
