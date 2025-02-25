import os

def get_account_list() :
    env = os.getenv('ACCOUNT_LIST')
    if not env:
        raise ValueError("环境变量 'ACCOUNT_LIST' 未设置或为空。")
    
    tmp = env.replace('&', '').split('#')
    for i in tmp:
        if i:
            info = i.split(';')
            if len(info) != 2:
                raise ValueError(f"环境变量 'ACCOUNT_LIST' 中的项格式不正确: {i}")
            yield info[0], info[1]

if __name__ == '__main__':
    try:
        for account, password in get_account_list():
            print(account, password)
    except ValueError as e:
        print(f"错误: {e}")
    except Exception as e:
        print(f"未知错误: {e}")
