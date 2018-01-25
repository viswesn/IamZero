import re


def str_join(*args):
    return ''.join(map(str, args))


def get_rclone_log_details(filename):
    patterns = ["Errors:", "Transferred:"]
    result = dict()
    result['log'] = filename
    with open(filename) as origin_file:
        for line in origin_file:
            for pattern in patterns:
                if re.match(pattern, line):
                    if pattern == "Transferred:":
                        result["Transferred"] = line[len(pattern):-1]
                        patterns.remove("Transferred:")
                    if pattern == "Errors:":
                        error_count = int(line[24:len(line) - 1])
                        result['Errors'] = error_count
                        patterns.remove("Errors:")
    return result


if __name__ == "__main__":
    print get_rclone_log_details("rclone1.log")