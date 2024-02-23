import csv
import os
import re


root = os.path.join(*os.path.dirname(os.path.abspath(__file__)).split("/")[:-3])
output = os.path.join("/" + root, "data", f"output.csv")
output_1 = os.path.join("/" + root, "data", f"output_1.csv")
result1 = os.path.join("/" + root, "data", f"result.log")
result2 = os.path.join("/" + root, "data", f"result2.log")
result1_1 = os.path.join("/" + root, "data", f"result_1.log")
result2_1 = os.path.join("/" + root, "data", f"result2_1.log")


def extract_ips_with_result_zero(file_path):
    ips_with_zero_result = []

    with open(file_path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            ip, port, result = row
            if result == "0":
                ips_with_zero_result.append(ip)

    return ips_with_zero_result


def extract_ips_from_log(file_path):
    ips = []

    with open(file_path, "r") as file:
        for line in file:
            match = re.search(r"\d+\.\d+\.\d+\.\d+", line)
            if match:
                ips.append(match.group())

    return ips


def find_ips_in_log_and_extract_lines(
    ips_to_find, log_file_path, log_file_path2, output_file_path
):
    extracted_lines = []

    with open(log_file_path, "r") as log_file:
        with open(log_file_path2, "r") as log_file2:

            for ip in ips_to_find:
                log_file.seek(0)
                # log_file2.seek(0)
                for line in log_file:
                    if ip in line:
                        extracted_lines.append(line)
                # for line in log_file2:
                #     if ip in line:
                #         extracted_lines.append(line)

    with open(output_file_path, "w") as output_file:
        output_file.writelines(extracted_lines)

    return len(extracted_lines)


def remove_duplicate_ips(input_file_path, output_file_path):
    unique_ips = set()
    rows_to_write = []

    with open(input_file_path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            ip = row[0]  # 假设IP地址在每行的第一个位置
            if ip not in unique_ips:
                unique_ips.add(ip)
                rows_to_write.append(row)

    with open(output_file_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows_to_write)


def remove_duplicate_ips_from_log(input_file_path, output_file_path):
    unique_ips = set()
    lines_to_write = []

    with open(input_file_path, "r") as file:
        for line in file:
            ip_match = re.search(r"\d+\.\d+\.\d+\.\d+", line)
            if ip_match and ip_match.group() not in unique_ips:
                unique_ips.add(ip_match.group())
                lines_to_write.append(line)

    with open(output_file_path, "w") as output_file:
        output_file.writelines(lines_to_write)

    return len(lines_to_write)


from collections import Counter


def count_results_in_csv(file_path):
    result_counts = Counter()

    with open(file_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            result_counts[row["result"]] += 1

    return result_counts


# ips_with_zero_result = extract_ips_with_result_zero(output_1)
# find_ips_in_log_and_extract_lines(ips_with_zero_result, result1_1, result2_1, "test.txt")
# # print(len(ips_with_zero_result))

result = count_results_in_csv(output_1)
print(result)
