#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scoring Program for Ranked Choice Voting

Created on Mon Apr 11 20:26:38 2022

@author: zackashm
"""

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt, rcParams
import seaborn
seaborn.set_theme(font_scale=4, rc={})


# import data
f = "/Users/zackashm/Downloads/Lab Preference Section 4.csv"
ranks = ["1st","2nd","3rd"]
data = pd.read_csv(f, header=0, names=ranks, usecols=[2,3,4])

# record the scores
scores = {"A":0,"B":0,"C":0,"D":0,"E":0}
ordered_scores = {r:scores.copy() for r in ranks}

# add up the total scores
for rank in ranks:
    for choice in data[rank]:
        scores[choice] += len(ranks) - ranks.index(rank)
        ordered_scores[rank][choice] += len(ranks) - ranks.index(rank)

# choosing the winner
def get_winner(score_dict, mask=None):
    # mask to focus only on select candidates (like previous-level winners)
    
    c,s = zip(*score_dict.items())
    choice = np.array(c)
    score = np.array(s)
    
    # extract winners indices
    if mask is None:
        max_score = score.max()
        winner_mask = score==max_score
    else:
        max_score = score[mask].max()
        winner_mask = np.logical_and(score==max_score, mask)
    
    winner = choice[winner_mask]
    
    return winner, winner_mask


# get the overall winner
winner, winner_mask = get_winner(scores)

print(*ordered_scores.items(),sep="\n")
print("Total: ", scores)
print("Overall winner: ", winner)

# handle if more than 1 overall winner
for rank in ranks:
    
    if len(winner)<1:
        raise ValueError("There are less than 1 winners. Something went wrong...")
    if len(winner) == 1:
        break
    
    print("Tied Winner")
    print("Trying ", rank, " rank winner...")
    
    # get new winner based on rank-specific score until 1 winner is left
    winner, winner_mask = get_winner(ordered_scores[rank], winner_mask)


max_score = scores[winner[0]]
print("Final winner: ", winner)

fig,axs = plt.subplots(figsize=[20,20])

plt.bar(*zip(*scores.items()), color="orange",edgecolor="black")
plt.text(winner, max_score+0.5, "Winner!", fontsize=rcParams["font.size"]*1,
         horizontalalignment='center',verticalalignment='center')
plt.ylabel("Scores")
plt.xlabel("Choices")