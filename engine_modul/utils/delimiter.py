POSSIBLE_DELIMITERS = [",", ":", ";", "\t"]


def find_delimiter(list_lines: list[str]):
    counts = {delimiter: 0 for delimiter in POSSIBLE_DELIMITERS}
    for line in list_lines:
        for delimiter in POSSIBLE_DELIMITERS:
            counts[delimiter] += line.count(delimiter)
    print(counts)
    sorted_counts = sorted([delimiter for delimiter in counts.keys()], key=lambda d: counts[d])
    print(sorted_counts)
    return sorted_counts[-1]
