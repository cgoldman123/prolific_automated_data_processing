import os, sys, re
import pandas as pd


if os.name == "nt":
    root = 'L:'
elif os.name == "posix":
    root = '/media/labs'

folders = {f'{root}/NPC/DataSink/StimTool_Online/WB_Cooperation_Task',f'{root}/NPC/DataSink/StimTool_Online/WB_Social_Media',
            f'{root}/NPC/DataSink/StimTool_Online/WB_Blind_Dating',f'{root}/NPC/DataSink/StimTool_Online/WB_Advice',f'{root}/NPC/DataSink/StimTool_Online/WB_Emotional_Faces',
            f'{root}/NPC/DataSink/StimTool_Online/WB_Emotional_Faces_CB',f'{root}/NPC/DataSink/StimTool_Online/WB_Social_Media_CB'}



def search_file(directory, pattern):
    for filename in os.listdir(directory):
        if pattern in filename:
            return os.path.join(directory, filename)
    return None

def check_attention_checks(file_path, question_checks):
    df = pd.read_csv(file_path,header=None)
    results = {}
    for key, (question, item) in question_checks.items():
        response = str(df.loc[df[0] == question, 1].values[0])
        results[key] = item in response
    return results

def session_checks(subject, patterns_checks):
    attention_checks = {}
    for folder in folders:
        for pattern, checks in patterns_checks.items():
            file = search_file(folder, f"{pattern}_{subject}")
            if file:
                checks_results = check_attention_checks(file, checks)
                attention_checks.update(checks_results)

    return attention_checks

def check_files(subject, session):
    flags={}
    results={}
    ses_surveys = {1: ('ryff_wb','sticsa_trait','sticsa_state',
        'well_being', 'qes_', 'panasx', 'ctq_'),
    2: ('csass_oecd', 'dpes_', 'health_questions', 'hils_', 'his_', 
        'indcol_', 'mhs_', 'pdsq_', 'stait_hope', 'swls_', 'trait_hope'),
    3: ('asi_', 'cit_', 'crt_7_', 'dast_10_', 'dts_', 'gfi_', 'hpq_',
        'lot_r_', 'maia_', 'mlq_', 'ncs_short', 'oasis_', 'pcl_5_', 'phq_8_', 'shs_',
        'tas_', 'vps_', 'wolf_'),
    4: ('bfi_', 'fss_', 'sbi_', 'stai_state', 'stai_trait', 'svs_',
        'teps_', 'upps_p', 'v_crt', 'vhs_', 'zan_srv'),
    5: ('bis_bas_', 'dfas_', 'leas_', 'promis_emotion',
        'promis_meaning', 'promis_self_efficacy', 'promis_self_efficacy_manage','promis_sleep', 'promis_social_iso',
        'promis_social_sat', 'whodas_')
    }
    files=[]
    for folder in folders:
        for f in os.listdir(folder):
            if f.__contains__(subject):
                files.append(f)

    for s in ses_surveys[session]:
        res = [x for x in files if re.search(s, x)]
        if len(res)==0:
            results[f'has_{s}_file'] = (False)
            flags.update(results)
    return(flags)


def check_questionnaires(subject, sessions_to_check):

    sessions = {
        1: ({
            'well_being': {
                'wb_attn1': ('question41_attention3', 'Item 4'),
                'wb_attn2': ('question42_attention9', 'Item 10'),
            },
            'ryff_wb': {
                'ryff_attn1': ('question16', 'Item 6'),
                'ryff_attn2': ('question30', 'Item 6'),
            },
            'panasx': {
                'panasx_attn1': ('question_check1', 'Item 4'),
                'panasx_attn2': ('question_check2', 'Item 4'),
            },
            'qes': {
                'quietego_attn1': ('question_check', 'Item 2'),
            },
        }),
        2: ({
            'trait_hope': {
                'future_attn1': ('question_check1', 'Item 4'),
            },
            'indcol': {
                'indcol_attn1': ('question_check1', 'Item 8'),
            },
            'dpes': {
                'dpes_attn1': ('question_check1', 'Item 6'),
            },
            'pdsq': {
                'pdsq_attn1': ('question_check1', '1'),
                'pdsq_attn2': ('question_check2', '1'),
            },
        }),
        3: ({
            'cit': {
                'cit_attn1': ('question_check1', 'Item 1'),
                'cit_attn2': ('question_check2', 'Item 5'),
            },
            'maia': {
                'maia_attn1': ('question_check1', '0'),
            },
            'wolf': {
                'wolf_attn1': ('question_check1', 'Item 3'),
            },
            'tas': {
                'tas_attn1': ('question_check1', 'Item 4'),
            },
        }),
        4: ({
            'sbi': {
                'sbi_attn1': ('question_check1', 'Item 6'),
            },
            'stai_state': {
                'stai_state1': ('question_check1', 'Item 4'),
            },
            'upps_p': {
                'uppsp1': ('question_check1', 'Item 1'),
                'uppsp2': ('question_check2', 'Item 1'),

            },
            'bfi': {
                'bfi1': ('question_check1', '2'),
            },
        }),
        5: ({
            'bis_bas': {
                'bis_bas1': ('question_check', 'Item 1'),
            },
            'promis_meaning': {
                'promis_meaning1': ('question_check1', '4'),
            },
            'whodas': {
                'whodas_attn1': ('question_check1', 'Item 5'),
            },
            'dfas': {
                'dfas_attn1': ('question_check1', 'Item 6'),
            },
        }),

    }
    total_attention_checks = {}
    for session in sessions_to_check:
        session_attention_checks = {key: False for check in sessions[session].values() for key in check}
        session_attention_checks.update(session_checks(subject, sessions[session]))
        all_files_present = check_files(subject, session)
        total_attention_checks.update(session_attention_checks)
        total_attention_checks.update(all_files_present)


    passed_all_checks = all(total_attention_checks.values())
    return passed_all_checks, total_attention_checks


#print(check_questionnaires("65fb5f438050e2495c957083",[3]))
#print(check_questionnaires("66290ede1ab02829b1c72509",[5]))

