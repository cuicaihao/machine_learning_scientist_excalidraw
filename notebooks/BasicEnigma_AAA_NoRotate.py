# %% [markdown]
# # Enigma A: How Enigma Works

# %% [markdown]
# ## Rotors

# %%
# create a function generatea random order of 26 letters
import random
import numpy as np
import pandas as pd

MAX_TRY = 1000_000
DEBUG = False

if DEBUG:
    CAPITAL_LETTERS = "ABCDEFGH"
    ROTOR_TOTAL = 2
else:
    CAPITAL_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ROTOR_TOTAL = 1

random.seed(MAX_TRY)


def create_rotors(rotor_total):
    # create a dataframe, use index as index, I as the alphabet column name
    index = list(CAPITAL_LETTERS)
    df_rotors = pd.DataFrame(index=index)
    for roter_i in range(rotor_total):
        try_cnt = 0
        alphabet = list(CAPITAL_LETTERS)
        while try_cnt < MAX_TRY:
            try_cnt += 1
            if try_cnt > MAX_TRY:
                print("Exceed max try")
                break
            else:
                alphabet = list(CAPITAL_LETTERS)
                random.shuffle(alphabet)
                differences = [i != j for i, j in zip(index, alphabet)]
                if all(differences):
                    break  # all True means: no same letter at the same positio, e.g. A->A, B->B
                else:
                    continue
        # create a dictionary to map the original letter to the new letter
        # dict_alphabet = dict(zip(index, alphabet))
        # print(alphabet)
        # convert roter_i into Roman number, e.g. I, II, III, IV, V
        roter_roman = ["I", "II", "III", "IV", "V"][roter_i]
        df_rotors[roter_roman] = alphabet
        # transpose the dataframe, so that the index becomes the column name
    df_rotors = df_rotors.T
    return df_rotors


df_rotors = create_rotors(rotor_total=ROTOR_TOTAL)
display(df_rotors)

# %% [markdown]
# ## Reflector


# %%
# Reflector is a special rotor, it does not rotate, it mapps the input to the output, e.g. A->Z, B->Y, C->X, etc.
# But No self mapping, e.g. A->A, B->B, C->C, etc.
# create 13 pairs from the 26 letters
def create_reflector():
    alphabet = list(CAPITAL_LETTERS)
    random.seed(MAX_TRY)  # set the seed for reproducibility
    random.shuffle(alphabet)
    pairs = [alphabet[i : i + 2] for i in range(0, len(alphabet), 2)]
    # convert paris into a dictionary
    pairs = dict(pairs)
    # revise the dictionary to make sure the value of the key is the key of the value
    pairs_revise = {}
    for k, v in pairs.items():
        pairs_revise[v] = k
    # merge the two dictionaries
    pairs.update(pairs_revise)
    # sort the dictionary by the key
    pairs = dict(sorted(pairs.items()))
    # save pairs to a dataframe
    df_reflector = pd.DataFrame(pairs, index=["reflector"])
    return df_reflector


df_reflector = create_reflector()
display(df_reflector)

# %% [markdown]
# ### rotor rerse mapping
#

# %%
# df_rotor reverse the order of the rows
df_rotors

# %%
df_temp = df_rotors.copy().transpose()
df_rotors_reverse = df_rotors.copy().transpose()
df_temp.reset_index(inplace=True)


for i in range(ROTOR_TOTAL):
    # select column index and rotor i column
    rotor_name = ["I", "II", "III", "IV", "V"][i]
    print(rotor_name)
    df_temp_pair = df_temp[["index", rotor_name]]

    # sort df_temp_pair by the roter_name column
    df_temp_pair = df_temp_pair.sort_values(by=rotor_name)
    # rename columns
    df_temp_pair.columns = [rotor_name, "index"]

    # delete the rotor_name column from df_rotors_reverse
    df_rotors_reverse = df_rotors_reverse.drop(columns=rotor_name)

    # add the column rotor_n    ame to the df_rotors_reverse
    df_rotors_reverse[rotor_name + "_r"] = df_temp_pair[rotor_name].values

    display(df_temp_pair)


df_rotors_reverse = df_rotors_reverse.transpose()


display(df_rotors_reverse)

# df_temp

# %%
# reverse the order of the of the df_rotors
df_rotors_reverse = df_rotors_reverse.iloc[::-1]

# stack the df_rotor and df_rotor_reverse horizontailly
df_rotor_reflector_encoder = pd.concat(
    [df_rotors, df_reflector, df_rotors_reverse], axis=0
)
df_rotor_reflector_encoder.reset_index(inplace=True)
# chent the index name to step
df_rotor_reflector_encoder.rename(columns={"index": "name"}, inplace=True)
df_rotor_reflector_encoder

# %%
engima_file = "engima.csv"
df_rotor_reflector_encoder.to_csv(engima_file, index=True)
# df_rotor_reflector_encoder

# %% [markdown]
# ## Encoder with Init Rotor Setting

# %%
from pathlib import Path

# load the engima_file file if it exists
if Path(engima_file).exists():
    df_engima = pd.read_csv(engima_file, index_col=0)
    display(df_engima)
else:
    print(f"{engima_file} does not exist")
    # create a new engima file


# %%
def mapping_letter(letter, df_engima):
    steps_total = df_engima.shape[0]
    letter_in = letter
    for step in range(steps_total):
        letter_out = df_engima[letter_in].values[step]
        # print(f'{step= : }    {letter_in} -> {letter_out}')
        letter_in = letter_out  # update: out -> in
    return letter_out


def test_mapping_letter(df_engima):
    for i, letter in enumerate(CAPITAL_LETTERS):
        # forwad mapping
        print(f"{i = }")
        letter_mapped = mapping_letter(letter, df_engima)
        print(f"forward:\t{letter} -> {letter_mapped}")
        letter2 = letter_mapped
        letter_mapped2 = mapping_letter(letter2, df_engima)
        print(f"backward:\t{letter2} -> {letter_mapped2}")

        assert letter == letter_mapped2, f"{letter} is not equal to {letter_mapped2}"


test_mapping_letter(df_engima)

# %%
init_rotor_position = "AAA"
plaintext = "The quick brown fox jumps over the lazy dog."


def format_input(plaintext):
    input = plaintext
    input = (
        input.upper()
        .replace(" ", "")
        .replace(".", "")
        .replace(",", "")
        .replace("!", "")
        .replace("?", "")
    )
    # convert into list
    return list(input)


def encode(plaintext, df_engima, init_rotor_position):
    input = format_input(plaintext)
    print(input)
    output = []
    # print(f'{input=}, {init_rotor_position=}')
    for i, letter in enumerate(input):
        # print(f'{i=}, {letter=}')
        output_letter = mapping_letter(letter, df_engima)
        output.append(output_letter)

    # list to string
    output = "".join(output)
    return output


ciphertext = encode(plaintext, df_engima, init_rotor_position)

print(f"{plaintext  =}")
print(f"{ciphertext =}")

message = encode(ciphertext, df_engima, init_rotor_position)
print(f"{ciphertext =}")
print(f"{message    =}")

# %%
