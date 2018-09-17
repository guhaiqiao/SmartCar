def encrypt(message=''):
    length = len(message)
    if length >= 0:
        # 设置异或校验位
        check = ord(message[0])
    else:
        return ''
    for i in range(1, length):
        check = check ^ ord(message[i])
    message += chr(check)
    return message


message = 'id:guhaiqiao'
print(encrypt(message))
