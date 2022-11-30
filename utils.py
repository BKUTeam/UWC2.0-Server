import json


def export_matrix_str_to_json(_matrix, _filename):
    rows = _matrix.split('\n')
    distance_matrix = [row.split("	") for row in rows]
    for i in range(0, len(distance_matrix)):
        for j in range(0, len(distance_matrix[0])):
            distance_matrix[i][j] = int(distance_matrix[i][j])

    with open("./data/{}".format(_filename), 'w') as wf:
        json.dump(distance_matrix, wf)


def print_matrix(_matrix):
    for i in _matrix:
        print('\t'.join(map(str, i)))