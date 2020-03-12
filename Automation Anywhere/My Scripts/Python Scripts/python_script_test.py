import sys

#Add each string
def append_string(str1, str2):
    """
    두개의 스트링을 합쳐서 되돌려 준다
    """
    result = str1 + " " + str2
    return result

#Define each business main function
def main(str1, str2, output_dir):
    """
    두개의 스트링을 합친후 파일에 저장한다.
    """
    added_string = append_string(str1, str2)
    with open(output_dir + "\" + "result.txt",'w',encoding = 'utf-8') as f:
        f.write(added_string + "\n")

if __name__ == "__main__":
    # 실행시 인수로 String1, String2, 결과저장 디렉토리명을 받는다.
    # 필요에 따라 인수는 sys.argv[4], sys.argv[5] 등 으로 추가 될 수 있다.
    main(sys.argv[1], sys.argv[2], sys.argv[3])

