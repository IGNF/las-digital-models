import laspy


def get_nb_points(path):
    """Get number of points in a las file"""
    with laspy.open(path) as f:
        nb_points = f.header.point_count

    return nb_points


def get_2d_bounding_box(path):
    """Get bbox for a las file (x, y only)"""
    with laspy.open(path) as f:
        mins = f.header.mins
        maxs = f.header.maxs

    return mins[:2], maxs[:2]


def get_classification_values(path):
    """Get the set of classification values existing in a las file"""
    with laspy.open(path) as f:
        las = f.read()
        classes = set(las.classification)

    return classes
