#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  4 20:43:53 2024

@author: johnnynienstedt
"""

#
# Investigation of Counts as Non-Markov States
#
# Johnny Nienstedt 11/4/24
#
# original hypothesis: z-swing% is lower on 3-1 after 3-0 than after 2-1
# result: no; however, zone% is higher after 3-0 vs after 2-1
#

import pandas as pd


classified_pitch_data = pd.read_csv('/Users/johnnynienstedt/Library/Mobile Documents/com~apple~CloudDocs/Baseball Analysis/Data/classified_pitch_data_v14')

count_data = classified_pitch_data[['game_year', 'batter', 'pitcher', 'game_date', 'at_bat_number', 'balls', 'strikes', 'swing_value', 'zone_value', 'woba_value', 'woba_denom']].copy()
count_data['pa_id'] = (count_data['batter'].astype(str) + '_' + 
                       count_data['pitcher'].astype(str) + '_' + 
                       count_data['game_date'].astype(str) + '_' + 
                       count_data['at_bat_number'].astype(str))
count_data = count_data[['game_year', 'pa_id', 'balls', 'strikes', 'swing_value', 'zone_value', 'woba_value', 'woba_denom']]

# select plate appearances that contain specified count(s)
def get_pas_with_counts(df, counts_required):

    # create masks for each required count
    masks = []
    for balls, strikes in counts_required:
        
        # get PAs that contain this count
        pas_with_count = df[
            (df['balls'] == balls) & 
            (df['strikes'] == strikes)
        ]['pa_id'].unique()
        masks.append(df['pa_id'].isin(pas_with_count))
    
    # combine masks to get PAs that contain ALL required counts
    final_mask = masks[0]
    for mask in masks[1:]:
        final_mask = final_mask & mask
    
    # filter the original DataFrame
    return df[final_mask].copy()

# compare the two immediate paths to a single count
def compare_paths(final_count):
    
    if final_count not in ['1-1', '1-2', '2-1', '2-2', '3-1', '3-2']:
        raise ValueError('Valid counts are: 1-1, 1-2, 2-1, 2-2, 3-1, 3-2')
    
    print("\nPaths to", final_count, "count:\n")
    
    b = int(final_count[0])
    s = int(final_count[2])
    
    count_1 = str(b-1) + '-' + str(s)
    count_2 = str(b) + '-' + str(s-1)
    
    from_ball = get_pas_with_counts(df=count_data, 
                                    counts_required=[(b,s), (b-1,s)])
    
    from_strike = get_pas_with_counts(df=count_data, 
                                      counts_required=[(b,s), (b,s-1)])
    
    zone_ball = round(100*from_ball.query('balls == @b and strikes == @s')['zone_value'].mean(), 1)
    zone_strike = round(100*from_strike.query('balls == @b and strikes == @s')['zone_value'].mean(), 1)
    
    zswing_ball = round(100*from_ball.query('balls == @b and strikes == @s and zone_value == 1')['swing_value'].mean(), 1)
    zswing_strike = round(100*from_strike.query('balls == @b and strikes == @s and zone_value == 1')['swing_value'].mean(), 1)
    
    oswing_ball = round(100*from_ball.query('balls == @b and strikes == @s and zone_value == 0')['swing_value'].mean(), 1)
    oswing_strike = round(100*from_strike.query('balls == @b and strikes == @s and zone_value == 0')['swing_value'].mean(), 1)
    
    woba_ball = round(from_ball.query('balls == @b and strikes == @s and woba_denom == 1.0')['woba_value'].mean(), 3)
    woba_strike = round(from_strike.query('balls == @b and strikes == @s and woba_denom == 1.0')['woba_value'].mean(), 3)
    
    df = pd.DataFrame(index = ['After ' + count_1, 'After ' + count_2], columns = ['Zone%', 'Z-Swing%', 'O-Swing%', 'wOBA'])
    df[df.columns[0]] = [zone_ball, zone_strike]
    df[df.columns[1]] = [zswing_ball, zswing_strike]
    df[df.columns[2]] = [oswing_ball, oswing_strike]
    df[df.columns[3]] = [woba_ball, woba_strike]
    
    print(df)
    
    if zone_ball > zone_strike + 0.5:
        p_agg = 'more'
    elif zone_ball < zone_strike - 0.5:
        p_agg = 'fewer'
    else:
        p_agg = 'a similar amount of'
        
    if zswing_ball > zswing_strike + 0.5:
        z_agg = 'more'
    elif zswing_ball < zswing_strike - 0.5:
        z_agg = 'less'
    else:
        z_agg = 'similarly'
      
    if oswing_ball > oswing_strike + 0.5:
        o_agg = 'more'
    elif oswing_ball < oswing_strike - 0.5:
        o_agg = 'less'
    else:
        o_agg = 'similarly'
    
    if woba_ball > woba_strike + 0.01:
        woba = 'better'
    elif woba_ball < woba_strike - 0.01:
        woba = 'worse'
    else:
        woba = 'about equally'

    if z_agg == o_agg:
        print('\nIn', final_count, 'counts after', count_1, 'counts, pitchers throw', p_agg, 'strikes compared to after ' + count_2 + '. Batters are', z_agg, 'agressive both in and out of the zone, and have performed', woba, 'overall.')
    
    else:
        print('\nIn', final_count, 'counts after', count_1, 'counts, pitchers throw', p_agg, 'strikes compared to after ' + count_2 + '. Batters are', z_agg, 'agressive in the zone but', o_agg, 'so out of the zone, and have performed', woba, 'overall.')