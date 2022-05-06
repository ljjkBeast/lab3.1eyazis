import time
import nltk
from nltk.corpus import wordnet as wn
from nltk.draw import TreeWidget
from nltk.draw.util import CanvasFrame
from tkinter import messagebox, Label, RIGHT, Frame, Tk, LEFT, Text, WORD, END, Menu, Button
from tkinter.filedialog import asksaveasfilename, askopenfilename

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('universal_tagset')
nltk.download('omw-1.4')

root = Tk()
root.option_add('*Dialog.msg.font', 'Helvetica 10')
root.title("Syntax parse tree")
root.resizable(width=True, height=True)

label_frame = Frame(root)
label_frame.pack()

enter_label = Label(label_frame, text='Enter text:', width=15)
enter_label.pack(side=LEFT)

empty_label = Label(label_frame, text='', width=84)
empty_label.pack(side=RIGHT)

enter_text = Text(width=80, height=20, wrap=WORD)
enter_text.pack()

canvas = CanvasFrame(root, width=700, height=200)
canvas.pack()


def open_file_and_input_text():
    file_name = askopenfilename(filetypes=(("Txt files", "*.txt"),))
    if file_name != '':
        text = open(file_name, 'r')
        enter_text.delete(1.0, END)
        enter_text.insert(1.0, text.read())
        text.close()

def save_txt():
    file = asksaveasfilename(filetypes=(("Txt file", "*.txt"),), defaultextension=("Txt file", "*.txt"))
    f = open(file,'w')
    f.write(enter_text.get(1.0, END))




help_info = """Natural language semantic analysis system
The system allows you to perform semantic analysis of English text, download text from a file, and save the text to a file in .txt format.
The result of the semantic analysis of the sentence is presented in the form of a tree, the nodes of which are lexemes and their definition, synonyms, antonyms, hyponyms and hypernyms.
To perform semantic analysis, you must enter text in the upper field and then click the "Draw" button.
To save, you must click the "Save" button, in the window that appears, select the desired file or specify a name for the new file.
To open the dictionary, you must click the menu item "Open", in the window that appears, select the desired file.
"""


def information():
    messagebox.askquestion("Help", help_info, type='ok')


def draw_semantic_tree():
    canvas.canvas().delete("all")
    start = time.time()
    text = enter_text.get(1.0, END)
    text = text.replace('\n', '')
    if text != '':
        sentences = nltk.sent_tokenize(text)
        enter_text.insert(END, '\n\nPlease waiting. Semantic tree is drawing...')
        root.update()
        result = '(S '
        for sent in sentences:
            sent = sent.replace('.', '')
            sent = sent.replace(',', '')
            sent = sent.replace('?', '')
            doc = nltk.word_tokenize(sent)
            result_sent = '(SENT '
            for word in doc:
                result_sent += get_word_semantic(word)
            result_sent += ')'
            result += result_sent
        result += ')'
        result = nltk.tree.Tree.fromstring(result)
        widget = TreeWidget(canvas.canvas(), result)
        canvas.add_widget(widget, 50, 10)

    finish = time.time()
    delta = finish - start
    enter_text.delete(enter_text.search('\n\nPlease waiting. Semantic tree is drawing...', 1.0, END), END)
    print('draw tree: ', delta)


def get_word_semantic(word: str) -> str:
    start = time.time()
    if len(wn.synsets(word)) == 0:
        return '(WS (W ' + word + '))'
    result = '(WS (W ' + word + ') (DEF ' + wn.synsets(word)[0].definition().replace(' ', '_') + ')'
    synonyms, antonyms, hyponyms, hypernyms = [], [], [], []
    word = wn.synsets(word)
    syn_app = synonyms.append
    ant_app = antonyms.append
    he_app = hyponyms.append
    hy_app = hypernyms.append
    for synset in word:
        for lemma in synset.lemmas():
            syn_app(lemma.name())
            if lemma.antonyms():
                ant_app(lemma.antonyms()[0].name())
    for hyponym in word[0].hyponyms():
        he_app(hyponym.name())
    for hypernym in word[0].hypernyms():
        hy_app(hypernym.name())
    if len(synonyms):
        result += ' (SYN '
        for synonym in synonyms:
            result += synonym + ' '
    if len(antonyms):
        result += ') (ANT '
        for antonym in antonyms:
            result += antonym + ' '
    if len(hyponyms):
        result += ') (HY '
        for hyponym in hyponyms:
            result += hyponym + ' '
    if len(hypernyms):
        result += ') (HE '
        for hypernym in hypernyms:
            result += hypernym + ' '
    result += '))'
    print('get word semantic', time.time() - start)
    return result


main_menu = Menu(root)
main_menu.add_command(label='Open', command=open_file_and_input_text)
main_menu.add_command(label='Save', command=save_txt)
main_menu.add_command(label='Draw', command=draw_semantic_tree)
main_menu.add_command(label='Help', command=information)
root.config(menu=main_menu)

root.mainloop()