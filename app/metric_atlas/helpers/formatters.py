from metric_atlas.helpers.models.Label import Label


def init_cap(input):
    return input.capitalize()


def get_label(input):
    if type(input) is dict:
        input = Label(
            name=input["name"],
            label=input["label"],
        )
        return input.label
    else:
        return input.label
