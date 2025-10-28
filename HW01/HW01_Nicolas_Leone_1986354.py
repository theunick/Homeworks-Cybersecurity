from pathlib import Path

ciphertext_path = Path(__file__).with_name("ciphertext.txt")
ciphertext = ciphertext_path.read_text()

# ciphertext replacing 'tt' letters with '\n' char for final plaintext
ciphertext_in_rows = ciphertext.replace("TT", "\n")

# ciphertext without 'tt' letters to work on frequency analysis
ciphertext_no_tt = ciphertext.replace("TT", "")

# count the occurrences of each letter in the TT-stripped ciphertext
ciphertext_letter_occurrences = {}
for char in ciphertext_no_tt:
    if char.isalpha() or char == " ":
        ciphertext_letter_occurrences[char] = ciphertext_letter_occurrences.get(char, 0) + 1

# sort by descending frequency so the most common letters come first
sorted_letter_occurrences = dict(
    sorted(ciphertext_letter_occurrences.items(), key=lambda entry: entry[1], reverse=True)
)

print("sorted letter occurrences: " + str(sorted_letter_occurrences) + "\n")

# expected frequency order (space first, then letters by common English usage - source: Wikipedia)
frequency_reference = [
    " ",
    "E",
    "T",
    "A",
    "O",
    "I",
    "N",
    "S",
    "R",
    "H",
    "L",
    "D",
    "C",
    "U",
    "M",
    "W",
    "F",
    "G",
    "Y",
    "P",
    "B",
    "V",
    "K",
    "J",
    "X",
    "Q",
    "Z",
]

# first attempt of frequency analysis decryption via frequency matching
sorted_cipher_chars = list(sorted_letter_occurrences.keys())
decryption_map = {
    cipher_char: frequency_reference[idx]
    for idx, cipher_char in enumerate(sorted_cipher_chars)
    if idx < len(frequency_reference)
}

print("decryption map: " + str(decryption_map) + "\n")

first_plaintext = "".join(
    decryption_map.get(char, char)
    for char in ciphertext_in_rows  
)

print("first plaintext:\n" + first_plaintext)

# being sure about the space frequency match, I manually try to adjust the results basing on common English words and patterns

# second attempt - swapping O with A since the O was frequently used as a single letter word, which is usually 'A' in English
second_plaintext = first_plaintext.translate(str.maketrans({"O": "A", "A": "O"}))
# print("second plaintext:\n" + second_plaintext)

# third attempt - swapping O with H since the word TOE is frequent in the text, and could be THE 
third_plaintext = second_plaintext.translate(str.maketrans({"O": "H", "H": "O"}))
# print("third plaintext:\n" + third_plaintext)

# fourth attempt - swapping O with N and L with D since the frequently used word AOL could be AND
fourth_plaintext = third_plaintext.translate(str.maketrans({"O": "N", "N": "O", "L": "D", "D": "L"}))
# print("fourth plaintext:\n" + fourth_plaintext)

# fifth attempt - swapping U with G beacuse EDUE could be EDGE since I see much words finished with -ED and I already fixed the letter E supposing it was correct call
fifth_plaintext = fourth_plaintext.translate(str.maketrans({"U": "G", "G": "U"}))
# print("fifth plaintext:\n" + fifth_plaintext)

# sixth attempt - swapping I with O since the word BEYIND could be BEYOND
sixth_plaintext = fifth_plaintext.translate(str.maketrans({"I": "O", "O": "I"}))
# print("sixth plaintext:\n" + sixth_plaintext)

# seventh attempt - swapping P with V since ABOPE could be ABOVE
seventh_plaintext = sixth_plaintext.translate(str.maketrans({"P": "V", "V": "P"}))
# print("seventh plaintext:\n" + seventh_plaintext)

# eighth attempt - swapping S with I since VSLLAGE could be VILLAGE
eighth_plaintext = seventh_plaintext.translate(str.maketrans({"S": "I", "I": "S"}))
# print("eighth plaintext:\n" + eighth_plaintext)

# ninth attempt - swapping R with S since the word HIR is frequently used and could be HIS
ninth_plaintext = eighth_plaintext.translate(str.maketrans({"R": "S", "S": "R"}))
# print("ninth plaintext:\n" + ninth_plaintext)

# tenth attempt - swapping M with F since the word LEMT could be LEFTL
tenth_plaintext = ninth_plaintext.translate(str.maketrans({"M": "F", "F": "M"}))
# print("tenth plaintext:\n" + tenth_plaintext)

# eleventh attempt - swapping C with W since CITH could be WITH and FOLLOCED could be FOLLOWED
eleventh_plaintext = tenth_plaintext.translate(str.maketrans({"C": "W", "W": "C"}))
# print("eleventh plaintext:\n" + eleventh_plaintext)

# twelfth attempt - swapping C with M since SCALL could be SMALL and AMROSS could be ACROSS
twelfth_plaintext = eleventh_plaintext.translate(str.maketrans({"C": "M", "M": "C"}))
#print("twelfth plaintext:\n" + twelfth_plaintext)

# final attempt - swapping K with P since STEK could be STEP and SKEAP could be SPEAK
final_plaintext = twelfth_plaintext.translate(str.maketrans({"K": "P", "P": "K"}))
print("final plaintext:\n" + final_plaintext)
