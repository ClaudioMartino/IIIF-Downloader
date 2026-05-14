import csv
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.colors import ListedColormap, LinearSegmentedColormap


# Global variables

file_path = 'docs/data.csv'

ylabels = ['1a', '1b', '1c', '2', '3a', '3b', '3c', '4a', '4b', '4c']

fail_color = 'firebrick'
fail_403_color = 'firebrick'
fail_404_color = 'firebrick'
fail_406_color = 'firebrick'
skipdb_color = '0.25'
skipns_color = '0.5'
ok_max_color = 'green'
ok_min_color = 'white'

cmap_size = 200  # Arbitrary value
fail_val = -int(cmap_size / 2)  # -100
fail_val_403 = fail_val + 5  # -95
fail_val_404 = fail_val + 10  # -90
fail_val_406 = fail_val + 15  # -85
skipdb_val = -int(cmap_size / 4) - int(cmap_size / 8)  # -75
skipns_val = -int(cmap_size / 4)  # -50
ok_max_val = -fail_val  # +100


# Functions

def csv_dict_to_list(csv_file):
    res1 = []
    res2 = []
    with open(csv_file, 'r') as data:
        for line in csv.DictReader(data):
            new_line = []
            new_line.append(line['1a'])
            new_line.append(line['1b'])
            new_line.append(line['1c'])
            new_line.append(line['2'])
            new_line.append(line['3a'])
            new_line.append(line['3b'])
            new_line.append(line['3c'])
            new_line.append(line['4a'])
            new_line.append(line['4b'])
            new_line.append(line['4c'])

            if (int(line['iiif_version']) == 2):
                res1.append(new_line)
            if (int(line['iiif_version']) == 3):
                res2.append(new_line)

    return res1, res2


def read_data(file_path):
    with open(file_path, 'r') as file:
        data = [line.strip().split(',') for line in file]
        return data


def normalize_data(data):
    # Read data
    normalized_data = []
    for row in data:
        normalized_row = [0] * len(row)
        max_value = 0
        for i, value in enumerate(row):
            if value == 'SKIP_DB':
                normalized_row[i] = skipdb_val
            elif value == 'SKIP_NS':
                normalized_row[i] = skipns_val
            elif value[:4] == 'FAIL':
                if value == 'FAIL_403':
                    normalized_row[i] = fail_val_403
                elif value == 'FAIL_404':
                    normalized_row[i] = fail_val_404
                elif value == 'FAIL_406':
                    normalized_row[i] = fail_val_406
                else:
                    normalized_row[i] = fail_val
            else:
                size = int(value[3:])  # Take N from OK_N
                normalized_row[i] = size
                if (size > max_value):  # Save max value for normalization
                    max_value = size

        # Normalization of N values (green)
        for i, value in enumerate(row):
            if (normalized_row[i] > skipns_val):
                normalized_row[i] *= ok_max_val
                normalized_row[i] /= max_value
        normalized_data.append(normalized_row)

    return normalized_data


def get_cmap():
    # Create empty cmap
    newcolors = [(0.0, 0.0, 0.0, 0.0)] * cmap_size

    # Create white-white-green cmap (white-green shade only in upper half, from cmap_size / 2 up)
    tmp_cmap = LinearSegmentedColormap.from_list("test", [ok_min_color, ok_min_color, ok_max_color], cmap_size)

    # Copy white-green values to upper half of cmap
    for i in range(int(cmap_size / 2), cmap_size):
        newcolors[i] = tmp_cmap(i)

    # Add red zones around failure levels
    margin = 2
    for i in range(0, 0 + margin):
        newcolors[i] = fail_color
    for i in range(5 - margin, 5 + margin):
        newcolors[i] = fail_403_color
    for i in range(10 - margin, 10 + margin):
        newcolors[i] = fail_404_color
    for i in range(15 - margin, 15 + margin):
        newcolors[i] = fail_406_color

    # Add gray around skip-done-before level (cmap_size / 8)
    for i in range(int(cmap_size / 8) - margin, int(cmap_size / 8) + margin):
        newcolors[i] = skipdb_color

    # Add gray around skip-not-suited level (cmap_size / 4)
    for i in range(int(cmap_size / 4) - margin, int(cmap_size / 4) + margin):
        newcolors[i] = skipns_color

    # Return final cmap
    return ListedColormap(newcolors)


def remove(data, skip):
    data2 = [line for k, line in enumerate(data) if k != skip]
    return data2


def add_ticks_and_labels(data, skip=None):
    rows = len(data)
    cols = len(data[0])

    # Y axis
    cnt = [0] * rows
    for i in range(rows):
        for j in range(cols):
            value = data[i][j]
            if (value > 0):
                cnt[i] += 1
    plt.yticks(ticks=range(rows), labels=[la + ' (' + str(cnt[i]) + ')' for i, la in enumerate(ylabels)])

    # X axis
    if (skip):
        plt.xticks(ticks=range(cols), labels=[i for i in range(cols + 1) if i != skip])
    else:
        plt.xticks(ticks=range(cols), labels=[i for i in range(cols)])


def add_texts(data):
    rows = len(data)
    cols = len(data[0])

    for i in range(rows):
        for j in range(cols):
            if (data[i][j] == fail_val):
                plt.text(j, i, '?', ha="center", va="center", fontsize='x-small')
            if (data[i][j] == fail_val_403):
                plt.text(j, i, 'x', ha="center", va="center", fontsize='x-small')
            if (data[i][j] == fail_val_406):
                plt.text(j, i, 'o', ha="center", va="center", fontsize='x-small')

            if (data[i][j] < ok_max_val and data[i][j] > skipns_val):
                ratio = "{:.1f}".format(data[i][j] / ok_max_val)
                if (ratio != "1.0"):
                    plt.text(j, i, ratio, ha="center", va="center", fontsize='x-small')


# Main

# Create cmap with custom colors
cmap = get_cmap()

# Create figure with 2 subplots
fig, (ax1, ax2) = plt.subplots(2, 1)
ax1.title.set_text('2.0/2.1 manifests')
ax2.title.set_text('3.0 manifests')

# Load data from file
data1, data2 = csv_dict_to_list(file_path)

# Add data to figure after normalization
skip1 = 19
data1 = normalize_data(data1)
data1 = remove(data1, skip1)
data1 = [list(row) for row in zip(*data1)]
ax1.imshow(data1, cmap=cmap, aspect="auto")

data2 = normalize_data(data2)
data2 = [list(row) for row in zip(*data2)]
ax2.imshow(data2, cmap=cmap, aspect="auto")

# Add ticks, labels and text
plt.sca(ax1)
add_ticks_and_labels(data1, skip1)
add_texts(data1)

plt.sca(ax2)
add_ticks_and_labels(data2)
add_texts(data2)

# Add legend
leg = [
    Patch(facecolor=ok_max_color, edgecolor='lightgray', label='Success, highest size'),
    Patch(facecolor=ok_min_color, edgecolor='lightgray', label='Success, lower size'),
    Patch(facecolor=skipns_color, edgecolor='lightgray', label='Skipped, not suited'),
    Patch(facecolor=skipdb_color, edgecolor='lightgray', label='Skipped, done before'),
    Patch(facecolor=fail_color, edgecolor='lightgray', label='Failure!'),
]
plt.legend(handles=leg, loc='upper center', bbox_to_anchor=(0.5, -0.25), ncols=3)

# Show everything
plt.tight_layout()
plt.show()
