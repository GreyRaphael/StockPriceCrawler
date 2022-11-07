import csv
import sys


def change_price(input_file, output_file):
    with open(input_file, 'r', encoding='utf8') as file_in:
        with open(output_file, 'w', encoding='utf8', newline='') as file_out:
            reader = csv.DictReader(file_in)
            writer = csv.DictWriter(file_out, reader.fieldnames)
            writer.writeheader()
            for record in reader:
                price = eval(record['f2'])
                new_price = round(price*(1+0.11), 2)
                # new_price = round(price*(1-0.11), 2)
                record['f2'] = new_price
                writer.writerow(record)


if __name__ == "__main__":
    argvs = sys.argv
    if len(argvs) == 1:
        input_file = 'output/sz00.csv'
        output_file = 'output/sz00-new-price.csv'
    elif len(argvs) == 2:
        input_file = argvs[1]
    elif len(argvs) == 3:
        input_file = argvs[1]
        output_file = argvs[2]
    else:
        print("too many arguments!")
        sys.exit(0)

    change_price(input_file, output_file)
    print('change prices successfully!')
