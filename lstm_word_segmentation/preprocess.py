from pathlib import Path
import numpy as np
from .accuracy import Accuracy
from collections import Counter
from .text_helpers import get_lines_of_text, compute_accuracy, add_additional_bars, compute_accuracy_best
from . import constants


def evaluate_existing_algorithms():
    # raw_path = Path.joinpath(Path(__file__).parent.parent.absolute(), 'Data/SAFT/test_raw.txt')
    # not_raw_path = Path.joinpath(Path(__file__).parent.parent.absolute(), 'Data/SAFT/test.txt')
    # add_additional_bars(raw_path, not_raw_path)

    # Use SAFT data set
    '''
    saft_icu_acc = compute_accuracy(not_raw_path, "icu")
    saft_deepcut_acc = compute_accuracy(not_raw_path, "deep")
    print("ICU accuracy on SAFT data     : BIES accuracy = {}, F1-score = {}".format(saft_icu_acc.get_bies_accuracy(),
                                                                                saft_icu_acc.get_f1_score()))
    print("Deepcut accuracy on SAFT data : BIES accuracy = {}, F1-score = {}".format(saft_deepcut_acc.get_bies_accuracy(),
                                                                                saft_deepcut_acc.get_f1_score()))
    '''

    # Use BEST data set
    best_icu_acc = compute_accuracy_best(starting_text=40, ending_text=45, algorithm="icu", exclusive=False)
    # best_deepcut_acc = compute_accuracy_best(starting_text=40, ending_text=45, algorithm="deep")
    print("ICU accuracy on BEST data     : BIES accuracy = {}, F1-score = {}".format(best_icu_acc.get_bies_accuracy(),
                                                                                best_icu_acc.get_f1_score()))
    # print("Deepcut accuracy on BEST data : BIES accuracy = {}, F1-score = {}".format(best_deepcut_acc.get_bies_accuracy(),
    #                                                                             best_deepcut_acc.get_f1_score()))


def preprocess_thai(verbose, exclusive):
    """
    This function uses the BEST data set to
        1) compute the grapheme cluster dictionary that holds the frequency of different grapheme clusters
        2) demonstrate the performance of icu word breakIterator and compute its accuracy
    Args:
        verbose: shows if we want to see how the algorithm is working or not
        exclusive: determines to use BEST data set or exclusive BEST data set where all non-Thai code points are
                   excluded
    """
    grapheme_clusters_dic = Counter()
    accuracy = Accuracy()
    for cat in ["news", "encyclopedia", "article", "novel"]:
        for text_num in range(1, 96):
            print(text_num)
            text_num_str = "{}".format(text_num).zfill(5)
            if exclusive:
                file = Path.joinpath(Path(__file__).parent.parent.absolute(), "Data/exclusive_Best/{}/{}_".format(cat, cat) +
                                     text_num_str + ".txt")
            else:
                file = Path.joinpath(Path(__file__).parent.parent.absolute(), "Data/Best/{}/{}_".format(cat, cat) +
                                     text_num_str + ".txt")

            lines = get_lines_of_text(file=file, type_of_lines="man_segmented")
            for line in lines:
                # Storing the grapheme clusters and their frequency in the dictionary
                grapheme_clusters_dic += line.get_grapheme_clusters()
                # Adding spaces manually once for each line, so they be identified as a major grapheme cluster
                if exclusive:
                    grapheme_clusters_dic += Counter({' ': 1})

                # Computing BIES corresponding to the manually segmented and ICU segmented
                true_bies = line.get_bies(segmentation_type="man")
                icu_bies = line.get_bies(segmentation_type="icu")

                # Computing the bies accuracy and F1 score using icu_bies_str and true_bies_str
                accuracy.update(true_bies=true_bies.str, est_bies=icu_bies.str)

                # Demonstrate how icu segmenter works
                if verbose:
                    line.display()

    graph_clust_freq = dict(grapheme_clusters_dic)
    graph_clust_freq = {k: v for k, v in sorted(graph_clust_freq.items(), key=lambda item: item[1], reverse=True)}
    graph_clust_ratio = graph_clust_freq
    total = sum(graph_clust_ratio.values(), 0.0)
    graph_clust_ratio = {k: v / total for k, v in graph_clust_ratio.items()}
    print("ICU BIES accuracy on BEST data is {}".format(accuracy.get_bies_accuracy()))
    print("ICU F1 accuracy on BEST data is {}".format(accuracy.get_f1_score()))
    save_file = Path.joinpath(Path(__file__).parent.parent.absolute(), "Data/Thai_graph_clust_ratio.npy")
    if exclusive:
        save_file = Path.joinpath(Path(__file__).parent.parent.absolute(), "Data/Thai_exclusive_graph_clust_ratio.npy")
    np.save(str(save_file), graph_clust_ratio)


def preprocess_burmese(verbose, exclusive):
    """
    This function uses the Google corpus crawler Burmese data set to
        1) Clean it by removing tabs from start of it
        1) Compute the grapheme cluster dictionary that holds the frequency of different grapheme clusters
        2) Demonstrate the performance of icu word breakIterator and compute its accuracy
    Args:
        verbose: shows if we want to see how the algorithm is working or not
        exclusive: determines to use BEST data set or exclusive BEST data set where all non-Thai code points are
                   excluded
    """
    grapheme_clusters_dic = Counter()
    if exclusive:
        file = Path.joinpath(Path(__file__).parent.parent.absolute(), "Data/my.txt")
    else:
        file = Path.joinpath(Path(__file__).parent.parent.absolute(), "Data/my.txt")  # use appropriate file here
    lines = get_lines_of_text(file=file, type_of_lines="man_segmented")
    for line in lines:
        # Storing the grapheme clusters and their frequency in the dictionary
        grapheme_clusters_dic += line.get_grapheme_clusters()
        # Adding spaces manually once for each line, so they be identified as a major grapheme cluster
        if exclusive:
            grapheme_clusters_dic += Counter({' ': 1})

        # Demonstrate how icu segmenter works
        if verbose:
            line.display()

    graph_clust_freq = dict(grapheme_clusters_dic)
    graph_clust_freq = {k: v for k, v in sorted(graph_clust_freq.items(), key=lambda item: item[1], reverse=True)}
    graph_clust_ratio = graph_clust_freq
    total = sum(graph_clust_ratio.values(), 0.0)
    graph_clust_ratio = {k: v / total for k, v in graph_clust_ratio.items()}

    save_file = Path.joinpath(Path(__file__).parent.parent.absolute(), "Data/Burmese_graph_clust_ratio.npy")
    if exclusive:
        save_file = Path.joinpath(Path(__file__).parent.parent.absolute(),
                                  "Data/Burmese_exclusive_graph_clust_ratio.npy")
    np.save(str(save_file), graph_clust_ratio)


def make_thai_burmese_dictionary():
    new_dic = Counter()
    for ch in constants.THAI_GRAPH_CLUST_RATIO.keys():
        new_dic[ch] += constants.THAI_GRAPH_CLUST_RATIO[ch]
    for ch in constants.BURMESE_GRAPH_CLUST_RATIO.keys():
        new_dic[ch] += constants.BURMESE_GRAPH_CLUST_RATIO[ch]
    new_dic = dict(new_dic)
    new_dic = {k: v for k, v in sorted(new_dic.items(), key=lambda item: item[1], reverse=True)}
    total = sum(new_dic.values(), 0.0)
    graph_clust_ratio = {k: v / total for k, v in new_dic.items()}
    save_file = Path.joinpath(Path(__file__).parent.parent.absolute(), "Data/Thai_Burmese_graph_clust_ratio.npy")
    np.save(str(save_file), graph_clust_ratio)
