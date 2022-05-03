"""
A module for processing Python sets
"""


def set_integration(set_list):
    """Function to make set integration iteratively
    
    Uses set properties for making integration of a list
    of sets

    Parameters
    ----------
    set_list : list of set
        

    Returns
    -------

    
    """
    out = []
    while len(set_list) > 0:
        first, *rest = set_list
        lf = -1
        while len(first) > lf:
            lf = len(first)
            rest2 = []
            for r in rest:
                if not first.isdisjoint(r):
                    first |= r
                else:
                    rest2.append(r)
            rest = rest2
        out.append(first)
        set_list = rest
    return out


def set_iter_union(key_mini_set, set_list):
    """Return a list of sets that where united according to a dictionary
    
    This function prevents that when creating a conex hull of a meta-city
    it intersects other polygons that initialy were not intersected. If
    this happens the new intersected polygon is added to the meta-city

    Parameters
    ----------
    key_mini_set : dict
        Dictionary that contains unique int keys and has sets as values
    set_list : list of sets
        List containing the initial sets in the list

    Returns
    -------

    
    """
    union_set = []
    for mini_set in set_list:
        i = True
        for key in mini_set:
            # If it is the first element a new set variable is created
            if i:
                union_mini_set = key_mini_set[key]
                i = False
            # On the other hand it is united with the next sets
            else:
                union_mini_set = union_mini_set.union(key_mini_set[key])
        union_set.append(union_mini_set)
    return union_set


def remove_set_duplicates(set_list):
    """ Returns a list of sets without duplicates

    Parameters
    ----------
    set_list : list of sets
        List containing the initial sets in the list
        

    Returns
    -------

    """
    new_list = list(set(frozenset(item) for item in set_list))
    new_list = list(map(set, new_list))
    return new_list
