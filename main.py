import math
import re
import shutil

from pandas import read_excel
from pandas import DataFrame
from matplotlib import pyplot
from PIL import Image


def draw_graph():
    pass


def fill_numbers_in_excel(excel_file_name, column_name):
    file = read_excel(excel_file_name)
    for i in range(0, len(list(file[column_name]))):
        file.at[file.index[i], "n"] = i + 1
    file.to_excel(excel_file_name, index=False)


def read_parameters_from_excel(excel_file_name, parameters_list):
    parameters_dictionary = {}
    file = read_excel(excel_file_name)
    for parameter in parameters_list:
        parameters_dictionary[parameter] = list(file[parameter])
    return parameters_dictionary


def calculate_distance_for_each_point(parameters_dictionary):
    point_distance_dictionary = {}
    print(parameters_dictionary)
    for i in range(0, len(list(dict(parameters_dictionary).values())[0])):
        current_point_end = list(dict(parameters_dictionary).values())[0][i]
        current_point_node = list(dict(parameters_dictionary).values())[1][i]
        print(f"current point end: {current_point_end}")
        point_distance_dictionary[f"{i + 1}"] = []
        for j in range(0, len(list(dict(parameters_dictionary).values())[0])):
            next_point_end = list(dict(parameters_dictionary).values())[0][j]
            next_point_node = list(dict(parameters_dictionary).values())[1][j]
            # print(f"next point end: {next_point_end}")
            point_distance_dictionary[f"{i + 1}"].append(math.sqrt(
                    (float(current_point_end) - float(next_point_end)) ** 2
                    + ((float(current_point_node) - float(next_point_node)) ** 2)
                )
            )
            distance = math.sqrt(((float(current_point_end) - float(next_point_end)) ** 2) + (((float(current_point_node) - float(next_point_node)) ** 2)))
            print(f"distance {distance} to point {next_point_end} {next_point_node}")
    return point_distance_dictionary


def find_min_distance_in_dictionary(point_distance_dictionary):
    min_value_dict = {}
    min_value = 9999
    point_from = ""
    point_to = ""
    for i in range(0, len(point_distance_dictionary)):
        current_dictionary = list(point_distance_dictionary.values())[i]
        for j in range(0, len(current_dictionary)):
            if current_dictionary[j] != 0 and current_dictionary[j] < min_value:
                min_value = current_dictionary[j]
                point_from = f"{i + 1}"
                point_to = f"{j + 1}"
    min_value_dict[point_from] = {}
    min_value_dict[point_from][point_to] = min_value

    # print(remove_min_value_connected_points_from_dict(point_distance_dictionary, point_from, point_to))
    return min_value_dict


def replace_in_parameters_dict(parameters_dict, min_value_dict):
    global clusters
    cluster = []

    point_from = list(dict(min_value_dict).keys())[0]
    point_to = list(dict(list(dict(min_value_dict).values())[0]).keys())[0]
    ends_list = list(list(dict(parameters_dict).values())[0])
    nodes_list = list(list(dict(parameters_dict).values())[1])

    cluster.append(point_from)
    cluster.append(point_to)
    clusters.append(cluster)
    print(f"clusters: {clusters}")

    ends_list_for_avg, nodes_list_for_avg = [], []
    ends_list_for_avg.append(ends_list.pop(int(point_from) - 1))
    ends_list_for_avg.append(ends_list.pop(int(point_to) - 2))
    nodes_list_for_avg.append(nodes_list.pop(int(point_from) - 1))
    nodes_list_for_avg.append(nodes_list.pop(int(point_to) - 2))

    print(ends_list_for_avg)
    print(nodes_list_for_avg)

    avg_values = find_avg_parameters(ends_list_for_avg, nodes_list_for_avg)

    ends_list.insert(int(point_from) - 1, avg_values[0])
    nodes_list.insert(int(point_from) - 1, avg_values[1])
    parameters_dict["end"] = ends_list
    parameters_dict["node"] = nodes_list
    return parameters_dict


def find_avg_parameters(ends_list_for_avg, nodes_list_for_avg):
    avg_values = [sum(list(ends_list_for_avg)) / len(list(ends_list_for_avg)),
                  sum(list(nodes_list_for_avg)) / len(list(nodes_list_for_avg))]
    return avg_values


# def get_euclidean_distance()


if __name__ == '__main__':
    clusters = []
    cluster_points = []
    # excel_file = read_excel("data_images.xlsx")
    # paths_list = list(excel_file["path"])
    fill_numbers_in_excel("data.xlsx", "end")
    fill_numbers_in_excel("data_images.xlsx", "z1")

    number_of_clusters = input("Input number of clusters: ")
    parameters_dictionary = read_parameters_from_excel("data.xlsx", ["end", "node"])
    distances_dictionary = {}
    for i in range(0, int(number_of_clusters)):
        # print(parameters_dictionary)
        # print(read_parameters_from_excel("data_images.xlsx", ["z1", "z2", "z3"]))
        # print(calculate_distance_for_each_point(parameters_dictionary))
        distances_dictionary = calculate_distance_for_each_point(parameters_dictionary)
        # print(find_min_distance_in_dictionary(distances))
        # replace_min_value_connected_points_in_dict_with_avg(parameters_dictionary, distances, find_min_distance_in_dictionary(distances))
        minimal_value_dictionary = find_min_distance_in_dictionary(distances_dictionary)
        parameters_dictionary = replace_in_parameters_dict(parameters_dictionary, minimal_value_dictionary)
    distances_dictionary = calculate_distance_for_each_point(parameters_dictionary)
    print(f"distances_dictionary: {distances_dictionary}")
    print(f"parameters_dictionary: {parameters_dictionary}")
