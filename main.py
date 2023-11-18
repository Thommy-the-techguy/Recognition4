import ast
import math
import re
import shutil

from pandas import read_excel
from pandas import DataFrame
from matplotlib import pyplot
from PIL import Image
from collections import OrderedDict


def draw_graph(clusters_with_coordinates_dictionary_default, classes_to_numbers_list, clusters_with_coordinates_final):
    data_dict = {"x": [], "y": []}
    available_colors = ["blue", "green", "red", "cyan", "magenta",
                        "yellow", "black", "#1E90FF", "#FFD700", "#FFA07A",
                        "#00FF00", "#BA55D3", "#FF6347", "#8B008B", "#FFC0CB",
                        "#FF69B4", "#00CED1", "#FF4500", "#9400D3", "#FF8C00"]
    colors_clusters_dict = {}
    for key in clusters_with_coordinates_dictionary_default:
        data_dict["x"].append(clusters_with_coordinates_dictionary_default[key][0])
        data_dict["y"].append(clusters_with_coordinates_dictionary_default[key][1])
    color_counter = 0
    for key in clusters_with_coordinates_final:
        colors_clusters_dict[available_colors[color_counter]] = ast.literal_eval(key)
        color_counter += 1
    for i in range(0, len(data_dict["x"])):
        pyplot.text(data_dict["x"][i], data_dict["y"][i], classes_to_numbers_list[i], ha="right", va="center")
    for key in colors_clusters_dict:
        for point in colors_clusters_dict[key]:
            pyplot.plot(clusters_with_coordinates_dictionary_default[str([point])][0],
                        clusters_with_coordinates_dictionary_default[str([point])][1],
                        color=key,
                        marker="o")
    colors_key_iterator = iter(colors_clusters_dict)
    plus_coordinates = calculate_plus_centers(clusters_with_coordinates_final,
                                              clusters_with_coordinates_dictionary_default)
    for coordinates in plus_coordinates:
        pyplot.plot(coordinates[0],
                    coordinates[1],
                    color=next(colors_key_iterator),
                    marker="+")
    pyplot.show()


def calculate_plus_centers(clusters_with_coordinates_final, clusters_with_coordinates_dictionary_default):
    plus_coords = []
    for key in clusters_with_coordinates_final:
        ends_list = []
        nodes_list = []
        for value in ast.literal_eval(key):
            ends_list.append(clusters_with_coordinates_dictionary_default[str([value])][0])
            nodes_list.append(clusters_with_coordinates_dictionary_default[str([value])][1])
        plus_coords.append(find_avg_parameters(ends_list, nodes_list))
    return plus_coords


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


def parse_numbers_to_clusters(excel_file_name, name_of_the_n_column):
    list_of_clusters = []
    file = read_excel(excel_file_name)
    for number in list(file[name_of_the_n_column]):
        list_of_clusters.append([number])
    return list_of_clusters


def get_cluster_plus_coordinates(list_of_clusters, parameters_dictionary):
    cluster_plus_coordinates_dict = {}
    for cluster, end, node in zip(list_of_clusters,
                                  list(list(dict(parameters_dictionary).values())[0]),
                                  list(list(dict(parameters_dictionary).values())[1])):
        cluster_plus_coordinates_dict[str(cluster)] = [end, node]
    return cluster_plus_coordinates_dict


def find_min_distance_between_clusters(cluster_plus_coordinates_dict):
    global ignore_this_points
    min_value = 9999
    cluster_from_to = []
    cluster_from = []
    cluster_to = []
    coordinates_list = []
    current_coordinates_list = []
    for i in range(0, len(cluster_plus_coordinates_dict)):
        comparable_key = list(dict(cluster_plus_coordinates_dict).keys())[i]
        coordinates = list(dict(cluster_plus_coordinates_dict)[comparable_key])
        # print(f"comparable key: {comparable_key}\ncoordinates: {coordinates}")
        for j in range(0, len(cluster_plus_coordinates_dict)):
            key = list(dict(cluster_plus_coordinates_dict).keys())[j]
            current_coordinates = list(dict(cluster_plus_coordinates_dict)[key])
            # print(current_coordinates)
            distance = get_distance(coordinates, current_coordinates)
            if current_coordinates != coordinates and distance < min_value and (
                    comparable_key not in ignore_this_points and key not in ignore_this_points):
                min_value = distance
                cluster_from_to = (ast.literal_eval(comparable_key) + ast.literal_eval(key))
                cluster_from = ast.literal_eval(comparable_key)
                cluster_to = ast.literal_eval(key)
                # print(f"cluster_from_to {cluster_from} {cluster_to} {min_value}")
                coordinates_list = coordinates
                current_coordinates_list = current_coordinates
        # print("\n")
    add_new_cluster_to_dict(cluster_from_to, coordinates_list, current_coordinates_list)
    add_to_ignore_list([cluster_from, cluster_to])
    reconstruct_dict(str(cluster_from), str(cluster_from_to))
    remove_not_merged([str(cluster_from), str(cluster_to)])
    # print(ignore_this_points)
    return cluster_from_to


def get_distance(coordinates_list, current_coordinates_list):
    summary = 0
    for i in range(0, len(coordinates_list)):
        summary += (float(coordinates_list[i]) - float(current_coordinates_list[i])) ** 2
    return math.sqrt(summary)


def add_new_cluster_to_dict(cluster_from_to, coordinates_list, current_coordinates_list):
    global clusters_w_coordinates_dict
    clusters_w_coordinates_dict[str(cluster_from_to)] = find_avg_parameters(coordinates_list, current_coordinates_list)


def add_to_ignore_list(cluster_from_to):
    global ignore_this_points
    for cluster in cluster_from_to:
        # print(f"cluster: {cluster}")
        if str(cluster) not in ignore_this_points:
            ignore_this_points.append(str(cluster))


def reconstruct_dict(comparable_key, cluster_from_to):
    global clusters_w_coordinates_dict
    keys_list, values_list = [], []
    temp_dict = {}
    for key in clusters_w_coordinates_dict:
        keys_list.append(key)
        values_list.append(clusters_w_coordinates_dict[key])
    index_for_key = keys_list.index(comparable_key)
    index_for_coords = 0
    for key in keys_list:
        if key == cluster_from_to:
            index_for_coords = keys_list.index(key)
            keys_list.remove(key)
            keys_list.insert(index_for_key, key)
            break
    temp_values = values_list.pop(index_for_coords)
    values_list.insert(index_for_key, temp_values)
    for key, values in zip(keys_list, values_list):
        temp_dict[key] = values
    clusters_w_coordinates_dict = temp_dict


def remove_not_merged(cluster_from_to):
    global clusters_w_coordinates_dict
    for cluster in cluster_from_to:
        clusters_w_coordinates_dict.pop(cluster)


def find_avg_parameters(ends_list_for_avg, nodes_list_for_avg):
    avg_values = [sum(list(ends_list_for_avg)) / len(list(ends_list_for_avg)),
                  sum(list(nodes_list_for_avg)) / len(list(nodes_list_for_avg))]
    return avg_values


def parse_classes_to_numbers(excel_file_name):
    classes_to_numbers_list = []
    file = read_excel(excel_file_name)
    classes = list(file["class"])
    for clazz in classes:
        if clazz == "first":
            classes_to_numbers_list.append("1")
        elif clazz == "second":
            classes_to_numbers_list.append("2")
        elif clazz == "third":
            classes_to_numbers_list.append("3")
    return classes_to_numbers_list


def fill_cluster_number_in_excel(excel_file_name, clusters_with_coordinates_dictionary):
    file = read_excel(excel_file_name)
    numbers = list(file["n"])
    for cluster in dict(clusters_with_coordinates_dictionary).keys():
        for number in numbers:
            if number in ast.literal_eval(cluster):
                file.at[file.index[number - 1], "cluster"] = (
                        list(dict(clusters_with_coordinates_dictionary).keys()).index(str(cluster)) + 1
                )
    file.to_excel(excel_file_name, index=False)


if __name__ == '__main__':
    ignore_this_points = []

    fill_numbers_in_excel("data.xlsx", "end")
    fill_numbers_in_excel("data_images.xlsx", "z1")

    number_of_clusters = input("Input number of clusters: ")
    clusters_w_coordinates_dict = get_cluster_plus_coordinates(
        parse_numbers_to_clusters("data.xlsx", "n"),
        read_parameters_from_excel("data.xlsx", ["end", "node"])
    )
    clusters_w_coordinates_dict_default = get_cluster_plus_coordinates(
        parse_numbers_to_clusters("data.xlsx", "n"),
        read_parameters_from_excel("data.xlsx", ["end", "node"])
    )
    amount_of_points = len(clusters_w_coordinates_dict)
    if int(number_of_clusters) > amount_of_points:
        exit(1)
    print(f"{len(clusters_w_coordinates_dict)} - {clusters_w_coordinates_dict}")
    for i in range(0, amount_of_points - int(number_of_clusters)):
        find_min_distance_between_clusters(clusters_w_coordinates_dict)
        print(f"{len(clusters_w_coordinates_dict)} - {clusters_w_coordinates_dict}")
    # print(f"ignore this points: {ignore_this_points}")
    # print(f"clusters w coordinates: {clusters_w_coordinates_dict}")
    # print(f"default {clusters_w_coordinates_dict_default}")
    draw_graph(clusters_w_coordinates_dict_default, parse_classes_to_numbers("data.xlsx"), clusters_w_coordinates_dict)
    calculate_plus_centers(clusters_w_coordinates_dict, clusters_w_coordinates_dict_default)
    fill_cluster_number_in_excel("data.xlsx", clusters_w_coordinates_dict)
