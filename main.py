import csv, datetime


class EmptyFov(Exception):
    pass


def csv_file_reader(filename: str) -> list:
    with open(filename) as fl:
        csv_file = csv.reader(fl, delimiter='\t')
        csv_file_data = list(csv_file)
    return csv_file_data


def filtering_dataset_by_columns(
        csv_file_data_list: list,
        *columns: str
) -> tuple[list[list[float]], dict[str, int]]:
    stars_params = []
    columns_position_indexes = {"id": 0}
    for col in columns:
        columns_position_indexes[col] = columns.index(col) + 1

    for i in range(2, len(csv_file_data_list)):
        try:
            stars_params.append(
                [float(csv_file_data_list[i][csv_file_data_list[1].index(col)])
                 for col in columns])
            stars_params[-1].insert(0, i - 1)
        except ValueError:
            raise ValueError("The cell is empty or has an invalid type of "
                             "value. Please check the dataset and the row - "
                             + str(i)) from None
    return stars_params, columns_position_indexes


def selecting_stars_in_fov(
        horizontal_view: float,
        vertical_view: float,
        object_ra: float,
        object_dec: float,
        stars_params: list,
        col_indexes: dict
) -> list:
    filtered_stars = []
    fov_right_edge = (object_ra + horizontal_view / 2) % 360
    fov_left_edge = (object_ra - horizontal_view / 2) % 360
    fov_upper_edge = (object_dec + vertical_view / 2) % 360
    fov_bottom_edge = (object_dec - vertical_view / 2) % 360

    if fov_upper_edge > 90:
        raise ValueError("The upper edge of fov cannot "
                         "be more than 90 degrees")
    elif fov_bottom_edge < -90:
        raise ValueError("The bottom edge of fov cannot "
                         "be less than -90 degrees")

    for i in range(len(stars_params)):
        is_the_star_in_fovh = (fov_left_edge < 0 and (
                360 + fov_left_edge <= stars_params[i][
            col_indexes["ra_ep2000"]] <= 360)) or \
                              (fov_left_edge >= 0 and (
                                      fov_left_edge <= stars_params[i][
                                  col_indexes["ra_ep2000"]] <= fov_right_edge))

        if is_the_star_in_fovh and fov_bottom_edge <= stars_params[i][
            col_indexes["dec_ep2000"]] <= fov_upper_edge:
            filtered_stars.append(stars_params[i])
    return filtered_stars


def sorting_by_column(
        list_to_be_sorted: list,
        column_name: str,
        col_indexes: dict
) -> list:
    for i in range(len(list_to_be_sorted) - 1):
        for j in range(len(list_to_be_sorted) - i - 1):
            if list_to_be_sorted[j][col_indexes[column_name]] > \
                    list_to_be_sorted[j + 1][col_indexes[column_name]]:
                list_to_be_sorted[j], list_to_be_sorted[j + 1] = \
                    list_to_be_sorted[j + 1], list_to_be_sorted[j]
    return list_to_be_sorted


def checking_if_there_is_stars_in_fov(
        stars_list: list,
        number_of_stars: int
) -> list:
    if stars_list:
        stars_list = stars_list[:number_of_stars]
        return stars_list
    else:
        raise EmptyFov("There are no stars in this fov, please try again")


def main():
    ra = float(input("Write Ra "))
    dec = float(input("Write Dec "))
    N = int(input("Write amount of stars "))
    fov_h = float(input("Write horizontal field of view "))
    fov_v = float(input("Write vertical field of view "))

    tsv_file = csv_file_reader("small_dataset.tsv")
    stars_parameters, columns_indexes = filtering_dataset_by_columns(
        tsv_file,
        "ra_ep2000",
        "dec_ep2000",
        "b"
    )
    stars_in_fov = selecting_stars_in_fov(
        fov_h,
        fov_v,
        ra,
        dec,
        stars_parameters,
        columns_indexes
    )
    stars_in_fov = sorting_by_column(stars_in_fov, "b", columns_indexes)
    stars_in_fov = checking_if_there_is_stars_in_fov(stars_in_fov, N)
    print(stars_in_fov)


if __name__ == "__main__":
    main()
