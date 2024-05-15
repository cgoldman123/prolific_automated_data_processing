import sys, os, re, warnings
import pandas as pd
import statistics as stats
import scipy.stats as scipy_stats
import numpy as np

warnings.filterwarnings('ignore')

#sub = sys.argv[1]
#tt = sys.argv[2]
if os.name == "nt":
    root_mini = 'L:/'
elif os.name == "posix":
    root_mini = '/media/labs/'
root = f'{root_mini}NPC/DataSink/StimTool_Online'

def task_checks(subject, task):
    flags = []
    filemissing=True
    try:
        if task.lower() == 'faces' or task.lower() == 'emotional_faces' or task.lower() == 'emotional faces':
            input_dir = f'{root}/WB_Emotional_Faces'
            for x in os.listdir(input_dir):
                if x.__contains__(subject) and x.__contains__('emotional_faces_v2'):
                    # check if the file was already found, in which case this is a duplicate
                    if filemissing == False:
                        flags.append('Subject has more than one behavioral file')
                    filemissing=False

                    file = pd.read_csv(f'{input_dir}/{x}')
                    start = max(file[file.trial_type=='MAIN'].index)
                    data = file[file.index > start]

                    rts = data.response_time[data.event_type==7]
                    sorted_rts = np.sort(rts)
                    if sorted_rts[-5] > 15:
                        flags.append(f"Suspiciously long RTS. Highest 5 RTs are {' '.join(map(str,np.round(sorted_rts[-5:],2)))}")
                    if max(rts) >60:
                        flags.append(f'Suspiciously long RT: {np.round(max(rts),2)} seconds')
                    if stats.mean(rts) > 2.5:
                        flags.append(f'Avg RT = {np.round(stats.mean(rts),3)}, may indicate not paying attention')
                    
                    incorrect_responses = sum(data.result[data.event_type==7]=='incorrect')
                    if  incorrect_responses> 150:
                        flags.append(f'Number of incorrect responses too high: {incorrect_responses}')
                    too_slow_responses = sum(data.result[data.event_type==7]=='too slow')
                    if  too_slow_responses> 100:
                        flags.append(f'Too slow on {too_slow_responses} trials')
                
                            

        elif task.lower() == 'advice' or task.lower() == 'advice_task': 
            input_dir = f'{root}/WB_Advice'
            for x in os.listdir(input_dir):
                if x.__contains__(subject) and x.__contains__('active_trust'):
                    if filemissing == False:
                        flags.append('Subject has more than one behavioral file')
                    filemissing=False

                    file = pd.read_csv(f'{input_dir}/{x}')
                    start = max(file[file.trial_type=='MAIN'].index)
                    data = file[file.index > start]
                    
                    blocks = [data.index[1]]
                    blocks.extend(data.index[data.event_type==3].values)

                    if max(data.trial) != 359:
                        flags.append(f'Participant has missing trials')

                    rts=[]
                    for t in range(360):
                        if 6 in data.event_type[data.trial==t].values:
                            choice = data.index[(data.trial==t) & (data.event_type==6)].values[0]
                            second = data.index[(data.trial==t) & (data.event_type==5)].values[-1]

                            rts.append(float(data.absolute_time[(data.trial==t) & (data.index==choice)].values-data.absolute_time[(data.trial==t) & (data.event_type==4)].values))
                            rts.append(float(data.absolute_time[(data.trial==t) & (data.event_type==8)].values-data.absolute_time[(data.trial==t) & (data.index==second)].values))
                        else:
                            rts.append(float(data.absolute_time[(data.trial==t) & (data.event_type==8)].values-data.absolute_time[(data.trial==t) & (data.event_type==5)].values))

                    rights=[]
                    lefts=[]
                    for b in range(0,len(blocks)):
                        if b==len(blocks)-1:
                            start=blocks[-1]
                            end=data.index[-1]
                        else:
                            start=blocks[b]
                            end=blocks[b+1]

                        temp = data[(data.index > start)&(data.index < end)]
                        rights.append(sum(temp.response[temp.event_type==8]=='right'))
                        lefts.append(sum(temp.response[temp.event_type==8]=='left'))

                    combined_list = rights+lefts
                    greater_than_27 = [ele for ele in combined_list if ele > 27]

                    if len(greater_than_27) >= 4:
                        flags.append(f'Response patterns on four or more blocks is more than 90% consistent')
                    sorted_rts = np.sort(rts)
                    if sorted_rts[-5] > 15:
                        flags.append(f"Suspiciously long RTS. Highest 5 RTs are {' '.join(map(str,np.round(sorted_rts[-5:],2)))}")
                    if max(rts) >60:
                        flags.append(f'Suspiciously long RT: {np.round(max(rts),2)} seconds')
                    if stats.mean(rts) > 2.5 or stats.mean(rts) < .1:
                        flags.append(f'Avg RT = {np.round(stats.mean(rts),3)}, may indicate not paying attention')
                    

        elif task.lower() == 'dating' or task.lower() == 'blind_dating' or task.lower() == 'blind dating': 
            input_dir = f'{root}/WB_Blind_Dating'
            for x in os.listdir(input_dir):
                if x.__contains__(subject) and x.__contains__('blind_dating'):
                    if filemissing == False:
                        flags.append('Subject has more than one behavioral file')
                    filemissing=False

                    file = pd.read_csv(f'{input_dir}/{x}')
                    start = max(file[file.trial_type=='MAIN'].index)
                    data = file[file.index > start]

                    rts = data.response_time[data.event_type==6].values
                    sorted_rts = np.sort(rts)
                    if sorted_rts[-5] > 15:
                        flags.append(f"Suspiciously long RTS. Highest 5 RTs are {' '.join(map(str,np.round(sorted_rts[-5:],2)))}")
                    if max(rts) >60:
                        flags.append(f'Suspiciously long RT: {np.round(max(rts),2)} seconds')
                    if stats.mean(rts) > 2.5 or stats.mean(rts) < .1:
                        flags.append(f'Avg RT = {np.round(stats.mean(rts),3)}, may indicate not paying attention')

        elif task.lower() == 'tom' or task.lower() == 'theory_of_mind' or task.lower() == 'theory of mind': 
            input_dir = f'{root}/WB_Theory_Of_Mind'
            for x in os.listdir(input_dir):
                if x.__contains__(subject) and x.__contains__('task'):
                    if filemissing == False:
                        flags.append('Subject has more than one behavioral file')
                    filemissing=False

                    file = pd.read_csv(f'{input_dir}/{x}')    

                    responses = file[file['Screen Name']=='Probe trial']
                    rnum = np.unique(list(map(int, responses['Spreadsheet Row'].values)))
                    trial = [False]*len(rnum)
                    resp_movement = [0]*len(rnum)

                    for i in range(len(rnum)):
                        if not responses[responses['Spreadsheet Row']==rnum[i]]['Zone Type'].values[0] in ['response_slider_firstInteraction', 'response_slider_initialValue']:
                            trial[i] = True
                        else:
                            if 'response_slider_firstInteraction' in responses[responses['Spreadsheet Row']==rnum[i]]['Zone Type'].values:
                                var = 'response_slider_firstInteraction'
                            elif 'response_slider_initialValue' in responses[responses['Spreadsheet Row']==rnum[i]]['Zone Type'].values:
                                var = 'response_slider_initialValue'
                        
                            resp_movement[i] = int(responses[(responses['Spreadsheet Row']==rnum[i]) & (responses['Zone Type']=='response_slider_endValue')]['Response'].values[0])-int(responses[(responses['Spreadsheet Row']==rnum[i]) & (responses['Zone Type']==var)]['Response'].values[0])  
                        
                    if len(rnum) < 60:
                        flags.append(f'File incomplete')                 
                    if sum(trial) >= 15: 
                        flags.append(f'Missing {sum(trial)} Trials!')
                    # if len(list(np.where(np.array(resp_movement)==0)[0])) >= 30:
                    #     flags.append(f"Didn't move slider on {len(list(np.where(np.array(resp_movement)==0)[0]))} trials!")
                          
        elif task.lower() == 'social media' or task.lower() == 'social' or task.lower() == 'social_media': 
            input_dir = f'{root}/WB_Social_Media'
            for x in os.listdir(input_dir):
                if x.__contains__(subject) and x.__contains__('social_media'):
                    if filemissing == False:
                        flags.append('Subject has more than one behavioral file')
                    filemissing=False
                    file = pd.read_csv(f'{input_dir}/{x}')
                    start = max(file[file.trial_type=='MAIN'].index)
                    data = file[file.index > start]
                    
                    trial_info = data[data.event_type==7]
                    rts = trial_info.response_time
                    choices = trial_info.response
                    if len(rts) != 560: 
                        flags.append('Missing Trials!')
                    sorted_rts = np.sort(rts)
                    if sorted_rts[-5] > 15:
                        flags.append(f"Suspiciously long RTS. Highest 5 RTs are {' '.join(map(str,np.round(sorted_rts[-5:],2)))}")
                    if max(rts) >60:
                        flags.append(f'Suspiciously long RT: {np.round(max(rts),2)} seconds')
                    if stats.mean(rts) > 2.5 or stats.mean(rts) < .1:
                        flags.append(f'Avg RT = {np.round(stats.mean(rts),3)}, may indicate not paying attention')

                    # if data.iloc[0,].trial_type  == "h1_Likes":
                    #     schedule = pd.read_csv(f'{root_mini}rsmith/lab-members/cgoldman/Wellbeing/social_media/schedules/sm_distributed_schedule1-counterbalanced.csv')
                    #     reward_diff = []
                    #     choice = []
                    #     for t in range(560):
                    #         if schedule.iloc[t,].force_pos == 'X':
                    #             # if the trial type _X, we know it's a free choice trial
                    #             schedule_info = schedule.iloc[t,]
                    #             # get the difference in generative means (left - right)
                    #             if trial_info.iloc[t,].trial_type == "h1_Likes" or trial_info.iloc[t,].trial_type == "h6_Likes":
                    #                 gen_diff = int(schedule_info.left_mean) - int(schedule_info.right_mean)
                    #             else:
                    #                 # for dislike trials we get the negative difference
                    #                 gen_diff = int(schedule_info.right_mean) - int(schedule_info.left_mean) 

                    #             reward_diff.append(gen_diff)
                    #             choice.append(choices.iloc[t])

                    #     reward_diff_left = [reward_diff[i] for i in range(len(reward_diff)) if choice[i] == "left"]
                    #     reward_diff_right = [reward_diff[i] for i in range(len(reward_diff)) if not choice[i]=="left"]
                    #     # Perform a two-sample t-test
                    #     t_stat, p_value = scipy_stats.ttest_ind(reward_diff_left, reward_diff_right, alternative='greater')
                        
                    #     if p_value > .05:
                    #         flags.append('No difference in generative means for correct/incorrect trials!')

        elif task.lower() == 'cooperation' or task.lower() == 'coop': 
            input_dir = f'{root}/WB_Cooperation_Task'
            for x in os.listdir(input_dir):
                if x.__contains__(subject) and x.__contains__('cooperation_task'):
                    if filemissing == False:
                        flags.append('Subject has more than one behavioral file')
                    filemissing=False
                    file = pd.read_csv(f'{input_dir}/{x}')
                    start = max(file[file.trial_type=='MAIN'].index)
                    data = file[file.index > start]
                    response_info = data[data.event_type==5]
                    stim_info =  data[data.event_type==4]
                    if (len(response_info) != 480) or (len(stim_info) != 480):
                        flags.append('Incorrect number of trials') 
                    else:
                        rts = np.array(response_info.absolute_time) - np.array(stim_info.absolute_time) 
                        sorted_rts = np.sort(rts)
                        
                        if sorted_rts[-5] > 15:
                            flags.append(f"Suspiciously long RTS. Highest 5 RTs are {' '.join(map(str,np.round(sorted_rts[-5:],2)))}")
                        if max(rts) >60:
                            flags.append(f'Suspiciously long RT: {np.round(max(rts),2)} seconds')
                        if stats.mean(rts) > 2.5 or stats.mean(rts) < .1:
                            flags.append(f'Avg RT = {np.round(stats.mean(rts),3)}, may indicate not paying attention')

                        # total_lose,total_win,win_shift,lose_stay = [0,0,0,0]
                        # for trial in range(1,480):
                        #     previous_result = response_info.iloc[trial-1].result
                        #     previous_response = response_info.iloc[trial-1].response
                        #     current_response = response_info.iloc[trial].response
                        #     if previous_result == 'positive':
                        #         total_win = total_win+1
                        #         if current_response != previous_response:
                        #             win_shift = win_shift+1
                        #     elif previous_result == 'negative':
                        #         total_lose = total_lose+1
                        #         if current_response == previous_response:
                        #             lose_stay = lose_stay+1
                        # win_shift_prop = win_shift/total_win
                        # lose_stay_prop = lose_stay/total_lose
                        # print(win_shift_prop)
                        # print(lose_stay_prop)
                            
                        # if win_shift_prop > .3:
                        #     flags.append(f"Win shift proportion is too high: {round(win_shift_prop,2)}")
                        # if lose_stay_prop > .4:
                        #    flags.append(f"Lose stay proportion is too high: {round(lose_stay_prop,2)}")
    except:
        flags.append('Exception thrown in task_checks script. Something is afoot.')
        
    if filemissing:
        flags.append('Behavioral File Not Found!')

    if len(flags) >= 1:
        status=[False,flags]
    else:
        status=[True,flags]
    return [status] 
    
# behavioral_checks = task_checks("tempi", "coop")
# print(behavioral_checks)