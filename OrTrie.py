#!/usr/bin/env python

# OrTrie Class: Provides a simple implementation of an ordinary tree using
#               Python dictionaries. Make/update, draw and search functions
#               have also been developed, but could require further development.

# Author: Lyudmil Vladimirov

import json
import string

from array import *
from django.utils.encoding import smart_str, smart_unicode
from nltk.tree import *
from nltk.draw import tree
from nltk.draw.util import CanvasFrame
from nltk.draw import TreeWidget

# Constant
INF = 999


class OrTrie():


    # =============================================================>
    # Creator func - get's called upon instantiation of an object
    # =============================================================>
    def __init__(self):
        self.root = dict()
        self.node_count = 0
        self.node_list = []
        self.distance = 0
        self.string_list = []
        self.W = ["#"]
        self.T = []
        for i in range(100):
            self.T.append([])
            for j in range(100):
                self.T[i].append(0)
                if (i == 0):
                    self.T[i][j] = INF
                elif(i == 1 and j != 0):
                    self.T[i][j] = j-1
                if (j == 0):
                    self.T[i][j] = INF
                elif (j == 1 and i!=0):
                    self.T[i][j] = i-1
        print self.T
        self.C = [1]
        self.results = dict()
        self.root_tree = Tree('root', [])


    # =============================================================>
    # make_list() func - Receives a text file as an input, splits
    #                    the words, removes punctiation and stores
    #                    words in a global list.OrTrie()
    # NOTE!: Similar preprocessing should be done on pattern before
    #        submitting a search query.
    # =============================================================>
    def make_list(self, in_file):
        self.string_list = []
        for line in in_file:
            for word in line.split():
                word = word.translate(string.maketrans("",""), string.punctuation)
                word = word.lower()
                word = unicode(word, errors = 'ignore')
                if (word) and word!='':
                    self.string_list.append(word)


    # =============================================================>
    # make_trie() func - Receives a word list and a file_no ID as
    #                    inputs and adds all words, including the
    #                    file ID to the global trie.
    # =============================================================>
    def make_trie(self, str_list, file_no):
        list_len = len(str_list)
        print "Making trie for file %s" %file_no
        for i in range(list_len):
            current_dict = self.root
            count = 0
            word = str_list[i]
            word = word + ' '
            word_matched = False
            for letter in word:
                no_match_key = True
                for key in current_dict.keys():
                    new_key = key
                    if word[count:] == key:
                        current_dict = current_dict.setdefault(word[count:], [])
                        if file_no not in current_dict:
                                current_dict.append(file_no)
                        word_matched = True
                        no_match_key = False
                        break
                    elif letter == key:
                        if letter ==' ':
                            current_dict = current_dict.setdefault(letter, [])
                            if file_no not in current_dict:
                                current_dict.append(file_no)
                        else:
                            current_dict = current_dict.setdefault(letter, {})
                        no_match_key = False
                        break
                    elif letter == key[0]:
                        new_key = key[1:]
                        temp_dict = {new_key: current_dict[key]}
                        del current_dict[key]
                        current_dict = current_dict.setdefault(letter, temp_dict)
                        no_match_key = False
                        break
                if no_match_key:
                    current_dict = current_dict.setdefault(word[count:],[file_no])
                    break
                elif word_matched:
                    break
                count+=1


    # =============================================================>
    # get_nltk_tree() func - Receives a trie and it's corresponding
    #                        root node as an input and outputs a
    #                        tree structure drawable by NLTK.
    # =============================================================>
    def get_nltk_tree(self, tree, root_node):
        child_list = []
        for node, value in tree.iteritems():
            if not " " in node:
                self.get_nltk_tree(value, node)
                child_tree = self.root_tree
            else:
                child_tree = Tree(node, []) # value instead of [] to print file_no
            child_list.append(child_tree)
        self.root_tree = Tree(root_node, child_list)


    # =============================================================>
    # draw_tree() func - Draws the trie created so far.
    # =============================================================>
    def draw_trie(self):
        self.root_tree.draw()


    # =============================================================>
    # get_results() func - Returns the results stored so far.
    # =============================================================>
    def get_results(self):
        return self.results


    # =============================================================>
    # reset_results() func - Clears any entries in the results list
    # =============================================================>
    def reset_results(self):
        self.results.clear()


    # =============================================================>
    # EditDist() func - Receives a level(int) and a pattern and
    # (H.Shang)*        computes the distance to the global (sub)word
    #                   read so far, by following the tree down the levels.
    # =============================================================>
    def EditDist(self, level, P):
        try:
            self.C[level] = 0
        except:
            self.C.append(0)
        #if level!=0:
            #last_C = self.C[level-1]
        #else:
            #last_C = 1
        for i in range(1, len(P)):
            x = int(i + 1)
            y = int(level + 1)
            s = 0 if (P[i] == self.W[level]) else 1
            r = 1 if (P[i-1] == self.W[level] and P[i] == self.W[level-1]) else INF
            self.T[x][y] = min(self.T[x][y-1]+1, self.T[x-1][y]+1, self.T[x-1][y-1]+s, self.T[x-2][y-2]+r)
            self.C[level] = (i) if (self.T[x][y] <= 1) else self.C[level]
        return (INF if (self.C[level]==0) else self.T[x-1][y])


    # =============================================================>
    # get_extensions() func - Receives a level(int) and a trie as
    #                         inputs and returns all the extensions
    #                         of the word ending at that trie level
    # =============================================================>
    def get_extensions(self, trie, level):
        for child_node, subtrie in trie.iteritems():
            try:
                self.W[level:(level+len(child_node)-1)] = child_node
            except:
                self.W.append(child_node)
            if isinstance(subtrie, dict):
                self.get_extensions(subtrie, level + 1)
            elif isinstance(subtrie, list):
                self.results[str("".join(self.W[ 1 : (level+len(child_node)-1)]))] = subtrie


    # =============================================================>
    # search() func - Receives a trie, it's root_node, a level(int)
    # (H. Shang)*     and a word pattern as inputs, searches through the
    #                 trie for any occurances of the approximate word
    #                 pattern and then stores them in a global list
    # =============================================================>
    def search(self, root_node, trie, level, pattern):
        if (" " in root_node):    # if (TrieNode in leaf node) then
            for character in root_node:
                character = smart_str(character)
                try:
                    self.W[level-1] = character
                except:
                    self.W.append(character)
                if (self.W[level-1] == " " and self.T[len(pattern)][level-1]<=1):
                    self.results[str("".join(self.W[ 1 : (level-1)]))] = trie
                    break
                self.distance = self.EditDist(level-1, pattern)
                if (self.distance == INF):
                    break
                level += 1
        else:
            for child_node, sub_trie in trie.iteritems():
                try:
                    self.W[level] = child_node[0]
                except:
                    self.W.append(child_node[0])
                if (str("".join(self.W[: (level+1)]))==pattern and len(child_node)!=2):
                    print "YES!"
                    self.get_extensions(trie[self.W[level]], level+1)
                    continue
                elif (self.W[level] == " " and self.T[len(pattern)][level]<=1):
                    self.get_extensions(trie, level)
                    continue
                self.distance = self.EditDist(level, pattern)
                if (self.distance == INF):
                    continue
                self.search(child_node, sub_trie, (level + 1), pattern)


# EXAMPLE FOR USE!!!!
# main() =================================================>
if __name__ == '__main__':
    j=0
    output = dict() # Create dictionary to store output
    or_trie = OrTrie() # Instantiate an ordinary trie

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # NOTE: The next two steps do not have to be run every time. It is only
    #       needed to create the trie once for each dataset and store it
    #       somewhere for future access.
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # STEP_1: Sample loop to go through all 845 files in MC1 article dataset (0-844.txt)
    for j in range(845):
        my_file = open("/home/sglvladi/Mini_Challenge_1/MC1_Data/articles/%s.txt"%(j), "r")
        or_trie.make_list(my_file) # make list of strings for file
        or_trie.make_trie(or_trie.string_list,j) # create/update trie

    # STEP_2: Store final trie (dictionary) in output file
    output_file = open("/home/sglvladi/Mini_Challenge_1/MC1_Data/tries/or_tries/groups/list_0-%s.txt"%(j),"w");
    output_file.write(json.dumps(or_trie.root, indent=4))
    output_file.close()

    # NOT ESSENTIAL: Code below is only needed to visually draw and store the
    #                obtained trie using the NLTK tree drawing package.
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~>
    #or_trie.get_nltk_tree(or_trie.root, 'root')
    #cf = CanvasFrame()
    #tc = TreeWidget(cf.canvas(),or_trie.root_tree)
    #cf.add_widget(tc,10,10)
    #cf.print_to_file('/home/sglvladi/Mini_Challenge_1/MC1_Data/tries/or_tries/groups/ps/0-%s_new.ps'%(j))
    #cf.destroy()
    #or_trie.draw_trie()
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~>

    # SEARCH_LOOP: Sample loop to allow user to repeatedly input a search
    # keyword, perform the required preprocessing of the keyword and initiate
    # an approximate search through the trie, returning any results acquired.
    while(True):
        print
        print "============================>"
        keyword = raw_input("Enter search keyword: ") # Get keyword from user

        # Perform identical keyword preprocessing as in make_list() func
        keyword = keyword.translate(string.maketrans("",""), string.punctuation)
        keyword = keyword.lower()
        keyword = unicode(keyword, errors = 'ignore')

        # !!!!ALWAYS!!!! Add "#" sign to head for the purpose of the algorithm
        keyword = "#"+ keyword

        # Search and print results
        print "Keyword to search: \"%s\""%(keyword)
        or_trie.reset_results() # Clear results list
        or_trie.search("root", or_trie.root , 1, keyword) # Search for keyword
        output = or_trie.get_results() # Extract results
        print
        print "Search complete!!"
        print
        print "Showing %i results:" %(len(output))
        for result in output.keys(): # Print results in a presentable format
            print
            print "Word: \"%s\"" % result
            print "Found in: %s" %output[result]

