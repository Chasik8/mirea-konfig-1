const = {}


def parse(text):
    if "var" in text:
        text = text.replace("var", "")
        text = text.replace(" ", "")
        stext = list(map(str, text.split('=')))
        if not len(stext) == 2:
            print("Ошибка объявления константы")
        name = stext[0]
        stext = stext[1]
        value=stext
        if "([" in stext and "])" in stext:
            stext = stext.split("([")[1]
            stext = stext.split(")]")[0]
            value={}
            for i in list(map(str, text.split(','))):
                test = list(map(str, i.split(':')))
                if not len(test) == 2:
                    print("Ошибка объявления словаря")
                nm, val = i.split(":")
                value[nm] = val
        elif "list(" in stext:
            stext = stext.split("list(")[1]
            stext = stext.split(")")[0]
            value=[]
            for i in list(map(str, stext.split(','))):
                value.append(i)
        const[name] = value
    elif "@{" in text:
        stext = text
        stext = stext.split("@{")[1]
        stext = stext.split("}")[0]
        if stext in const:
            if type(const[stext]) == str:
                const[stext] = eval(const[stext])
    else:
        print("Ошибка")

def main():
    text = list(map(str, input().split(";")))
    for i in text:
        if "||" in i:
            ii = i.split("||")[0]
        else:
            ii=i
        if not ii == '':
            parse(ii)
    print("<root>")
    for i in const:
        if type(const[i])==dict:
            print(f"    <dict name={i}>")
            for j in const[i]:
                print(f"        <key> {j} </key>")
                print(f"        <value> {const[i][j]} </value>")
            print(f"    </dict>")
        elif type(const[i])==list:
            print(f"    <list name={i}>")
            for j in const[i]:
                print(f"        <value> {j} /value>")
            print(f"    </list>")
        else:
            print(f"    <value name={i}> {const[i]} </value>")
    print("</root>")

if __name__ == "__main__":
    main()

