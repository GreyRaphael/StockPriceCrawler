import sys
from PriceCrawler import PriceProvider

def get_codelist(stock_file):
    code_list = []
    with open(stock_file, "r", encoding="utf8") as file:
        for line in file:
            code = line.rstrip("\n")
            if code.startswith("0") or code.startswith("3"):
                code_list.append({"SECUCODE": f"{code}.SZ"})
            elif code.startswith("6"):
                code_list.append({"SECUCODE": f"{code}.SH"})
    return code_list

if __name__ == "__main__":
    stockfile = "input/zz500.txt"
    seperate_num = 2

    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 2:
        stockfile = sys.argv[1]
    elif len(sys.argv) == 3:
        stockfile = sys.argv[1]
        seperate_num = int(sys.argv[2])
    else:
        print("to many arguments")
        sys.exit(0)
    
    code_list = get_codelist(stockfile)
    print("begin crawler")
    obj = PriceProvider(code_list)
    share_list = obj.get_sharelist()
    share_list.sort(key=lambda x: x['cost'])
    print('end crawler')

    # write2csv
    print(f"share list length={len(share_list)}")
    combined_list=obj.seperateList(share_list, N=seperate_num, writeFlag=False)
    obj.writeCSV("output/shares.csv", combined_list)
