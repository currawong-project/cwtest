import csv
import copy

def no_cvt(x):
    return x

def int_cvt( x):
    return int(x) if x else None

def float_cvt(x):
    return float(x) if x else None

def parse_csv( fname ):

    rowL = []
    cvtD = {"opcode":no_cvt,
                  "meas":int_cvt,
                  "index":int_cvt,
                  "voice":int_cvt,
                  "loc":int_cvt,
                  "eloc":int_cvt,
                  "oloc":int_cvt,
                  "tick":int_cvt,
                  "sec":float_cvt,
                  "dur":float_cvt,
                  "rval":float_cvt,
                  "dots":int_cvt,
                  "sci_pitch":no_cvt,
                  "dmark":no_cvt,
                  "dlevel":int_cvt,
                  "status":int_cvt,
                  "d0":int_cvt,
                  "d1":int_cvt,
                  "bar":int_cvt,
                  "section":int_cvt,
                  "bpm":int_cvt,
                  "grace":no_cvt,
                  "tie":no_cvt,
                  "onset":no_cvt,
                  "pedal":no_cvt,
                  "dyn":no_cvt,
                  "even":no_cvt,
                  "tempo":no_cvt}


    sostN = 0
    dampN = 0
    
    with open(fname) as f:
        rdr = csv.DictReader(f)

        for row in rdr:

            r = { label:cvtD[label](val) for label,val in row.items() }

            if r['opcode'] == 'ped':
                if r['d0'] == 64:
                    dampN += 1
                else:
                    sostN ++ 1

            
            rowL.append(r)

    print('damp:',dampN,'sost:',sostN);
    return rowL

def gen_cut_list( rowL, meas_cutL ):

    cutL            = []    
    in_sect_flag    = False
    sectL_idx        = 0
    beg_cut_row_idx = None
    
    for i,r in enumerate(rowL):

        if r['opcode'] == 'bar':

            if not in_sect_flag and r['meas'] == meas_cutL[sectL_idx][0]:
                in_sect_flag = True
                beg_cut_row_idx = i
                
            elif in_sect_flag and r['meas'] == (meas_cutL[sectL_idx][1]+1):
                in_sect_flag = False

                cutL.append( (meas_cutL[sectL_idx][0], meas_cutL[sectL_idx][1], beg_cut_row_idx, i+1) )
                sectL_idx += 1

                if sectL_idx >= len(meas_cutL):
                    break
    
    return cutL


def print_approx_cut_list( rowL, approx_cutL ):

    for cut in approx_cutL:
        print( rowL[cut[2]]['meas'],rowL[cut[2]]['loc'], rowL[cut[3]]['meas'],rowL[cut[3]]['loc'] )


def gen_gate_matrices( rowL ):

    noteM    = []
    pedalM   = []
    damp_idx = 0
    sost_idx = 1

    noteStateL  = [False]*128
    pedalStateL = [False]*2

    note_on_cnt = 0
    pedal_on_cnt = 0
    note_off_cnt = 0
    pedal_off_cnt = 0
    
    for i,r in enumerate(rowL):
        if r['opcode'] == 'non' and r['d0']:
            noteStateL[r['d0']] = True
            note_on_cnt += 1
            
        elif r['opcode'] == 'nof':
            noteStateL[r['d0']] = False
            note_off_cnt += 1
            
        elif r['opcode'] == 'ped':
            down_fl = r['d1']!=0
            ped_idx = damp_idx if r['d0']==64 else sost_idx
            pedalStateL[ped_idx] = down_fl

            if down_fl:
                pedal_on_cnt += 1
            else:
                pedal_off_cnt += 1

        noteM.append(copy.copy(noteStateL))
        pedalM.append(copy.copy(pedalStateL))

    print("notes:",note_on_cnt,note_off_cnt,"pedals:",pedal_on_cnt,pedal_off_cnt)
    return noteM, pedalM
            
def insert_off_message( xL, gateL, opcode ):

    cnt = 0
    
    # take the first note-off row as a prototype note off record
    proto_row = None
    for r in xL:
        if r['opcode'] == opcode:
            proto_row = copy.copy(r)
            proto_row['meas']  = xL[-1]['meas']
            proto_row['sec']   = xL[-1]['sec']
            proto_row['tick']  = 0;
            proto_row['d0']    = 0;
            break;
        
    for i,flag in enumerate(gateL):
        if flag:

            proto_row['index'] = xL[-1]['index'] + 1
            
            if opcode == 'nof':
                proto_row['d0'] = i
                
            elif opcode == 'ped':
                proto_row['d1'] = 64 if i==0 else 66
                        
            xL.append( copy.copy(proto_row) )
            cnt += 1

    return cnt


def fix_meas_numbers( rowL ):
    meas = 1

    src_measL = sorted(set([ r['meas'] for r in rowL]))
    meas_mapD = { meas:i+1 for i,meas in enumerate(src_measL) }

    for row in rowL:
        row['meas'] = meas_mapD[ row['meas'] ]

            
        
        
def gen_raw_output_list( rowL, cutL, noteM, pedalM ):

    def _update_secs( rL, base_secs ):
        dsec = 0.0
        sec0 = None
        sec = 0
        for i,r in enumerate(rL):
            if r['sec']:
                if sec0:
                    dsec = r['sec'] - sec0
                sec0 = r['sec']
            sec += dsec
            r['sec'] = sec + base_secs      

    outL = []

    base_secs = 0.0
    
    for b_meas,e_meas,bri,eri in cutL:

        xL = rowL[bri:eri]
        note_cnt  = insert_off_message(xL,noteM[eri-1],'nof')
        pedal_cnt = insert_off_message(xL,pedalM[eri-1],'ped')

        _update_secs(xL,base_secs)

        base_secs = xL[-1]['sec']
        
        outL += xL

        print(b_meas,e_meas,note_cnt,pedal_cnt,xL[-1]['opcode'])
        
    return outL    
    

def write_output_file( fname, rowL ):
    
    fieldnamesL = ["opcode","meas","index","voice","loc","eloc","oloc","tick","sec","dur","rval","dots","sci_pitch","dmark","dlevel","status","d0","d1","bar","section","bpm","grace","tie","onset","pedal","dyn","even","tempo"]

    with open(fname,"w") as f:
        wtr = csv.DictWriter(f,fieldnamesL)

        wtr.writeheader()
        for r in rowL:
            wtr.writerow(r)

        
if __name__ == "__main__":
    """
    1 - 7
    215 - 218
    241 - 247
    272 - 283
    290 - 295 (first beat of 290 is converted to a rest)
    333 - 343
    352 - 365 (tie to first note in 352 is deleted)
    375 - 391
    398 - 400
    405 - 433 (last chord is converted to whole notes with fermata, measure is now 9/4)
    11m

    
    """

    meas_cutL = [
        (1,7),
        (215,218),
        (241,247),
        (272,283),
        (290,295),
        (333,343),
        (352,365),
        (375,391),
        (398,400),
        (405,433)
        ]
                              
    in_fname = "/home/kevin/src/cwtest/src/cwtest/cfg/gutim_full/data/score/20231028/temp.csv"
    out_fname = "10_min_demo.csv"


    rowL = parse_csv(in_fname)
    
    cutL = gen_cut_list(rowL,meas_cutL)

    print_approx_cut_list(rowL,cutL)
    
    if True:

        noteM, pedalM = gen_gate_matrices( rowL )

        outL = gen_raw_output_list( rowL, cutL, noteM, pedalM )

        fix_meas_numbers(outL)

        write_output_file(out_fname,outL)
