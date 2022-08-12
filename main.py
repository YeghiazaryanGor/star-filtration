import csv, datetime


class EmptyFov(Exception):
    pass


def csv_file_reader(filename: str) -> list:
    with open(filename) as fl:
        csv_file = csv.reader(fl, delimiter='\t')
        csv_file_data = list(csv_file)
    return csv_file_data


def filtering_dataset_by_columns(
        datalist: list,
        *columns: str
) -> tuple[list[list[float]], dict[str, int]]:
    stars_list = []
    columns_position_indexes = {"id": 0}
    for col in columns:
        columns_position_indexes[col] = columns.index(col) + 1

    for i in range(2, len(datalist)):
        try:
            star = [float(datalist[i][datalist[1].index(col)]) for col in
                    columns]
            stars_list.append(star)
            stars_list[-1].insert(0, i - 1)
        except ValueError:
            raise ValueError("The cell is empty or has an invalid type of "
                             "value. Please check the dataset and the row - "
                             + str(i)) from None
    return stars_list, columns_position_indexes


def selecting_stars_in_fov(
        horizontal_view: float,
        vertical_view: float,
        obj_ra: float,
        obj_dec: float,
        stars_list: list,
        col_indexes: dict
) -> list:
    filtered_stars = []
    fov_right_edge = (obj_ra + horizontal_view / 2) % 360
    fov_left_edge = (obj_ra - horizontal_view / 2) % 360
    fov_upper_edge = (obj_dec + vertical_view / 2) % 360
    fov_bottom_edge = (obj_dec - vertical_view / 2) % 360

    if fov_upper_edge > 90:
        raise ValueError("The upper edge of fov cannot "
                         "be more than 90 degrees")
    elif fov_bottom_edge < -90:
        raise ValueError("The bottom edge of fov cannot "
                         "be less than -90 degrees")

    for i in range(len(stars_list)):
        ra_index = col_indexes["ra_ep2000"]
        dec_index = col_indexes["dec_ep2000"]
        less_than_zero = fov_left_edge < 0 and (
                360 + fov_left_edge <= stars_list[i][ra_index] <= 360)
        more_than_zero = fov_left_edge >= 0 and (
                fov_left_edge <= stars_list[i][ra_index] <= fov_right_edge)
        is_in_horizontal_fov = less_than_zero or more_than_zero

        if is_in_horizontal_fov and \
                fov_bottom_edge <= stars_list[i][dec_index] <= fov_upper_edge:
            filtered_stars.append(stars_list[i])
    return filtered_stars


def sorting_by_column(
        to_be_sorted: list,
        column_name: str,
        col_indexes: dict
) -> list:
    for i in range(len(to_be_sorted) - 1):
        for j in range(len(to_be_sorted) - i - 1):
            col = col_indexes[column_name]
            if to_be_sorted[j][col] > to_be_sorted[j + 1][col]:
                to_be_sorted[j], to_be_sorted[j + 1] = to_be_sorted[j + 1], \
                                                       to_be_sorted[j]
    return to_be_sorted


def checking_if_there_is_stars_in_fov(
        stars_list: list,
        number_of_stars: int
) -> list:
    if stars_list:
        stars_list = stars_list[:number_of_stars]
        return stars_list
    else:
        raise EmptyFov("There are no stars in this fov, please try again")


def adding_new_column(col_name: str, col_indexes: dict):
    col_indexes[col_name] = len(col_indexes)
    return col_indexes


def calculating_distance(
        stars_list: list,
        object_ra: float,
        object_dec: float,
        col_indexes: dict
) -> list:
    for i in range(len(stars_list)):
        temp_ra = stars_list[i][col_indexes["ra_ep2000"]]
        temp_dec = stars_list[i][col_indexes["dec_ep2000"]]
        distance = ((object_ra - temp_ra) ** 2 +
                    (object_dec - temp_dec) ** 2) ** 0.5
        stars_list[i].append(distance)

    return stars_list


def getting_todays_timestamp() -> float:
    current_time = datetime.datetime.now()
    current_timestamp = current_time.timestamp()
    return current_timestamp


def output_csv_file_creation(stars_list: list, head: list, timestamp: float):
    with open(str(timestamp) + ".csv", "w") as fl:
        writer = csv.writer(fl)
        writer.writerow(head)
        writer.writerows(stars_list)


def main():
    ra = float(input("Write Ra "))
    dec = float(input("Write Dec "))
    N = int(input("Write amount of stars "))
    fov_h = float(input("Write horizontal field of view "))
    fov_v = float(input("Write vertical field of view "))

    tsv_file = csv_file_reader("small_dataset.tsv")
    stars_list, columns_indexes = filtering_dataset_by_columns(
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
        stars_list,
        columns_indexes
    )
    stars_in_fov = sorting_by_column(stars_in_fov, "b", columns_indexes)
    stars_in_fov = checking_if_there_is_stars_in_fov(stars_in_fov, N)
    columns_indexes = adding_new_column("distance", columns_indexes)
    stars_in_fov = calculating_distance(
        stars_in_fov,
        ra,
        dec,
        columns_indexes)
    stars_in_fov = sorting_by_column(stars_in_fov, "distance", columns_indexes)
    header = ["Id", "Ra", "Dec", "Brightness", "Distance"]
    current_timestamp = getting_todays_timestamp()
    output_csv_file_creation(stars_in_fov, header, current_timestamp)


if __name__ == "__main__":
    main()
