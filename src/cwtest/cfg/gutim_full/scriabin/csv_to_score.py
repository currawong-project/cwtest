import csv,json,os

def parse_score( score_fn ):

    scoreL = []
    with open(score_fn) as f:
        rdr = csv.DictReader(f)

        for r in rdr:
            scoreL.append(dict(r))
            
    return scoreL    


def invert_velocity( d1 ):

    tbl =  [ 1,1,2,2,3,5,8,10,13,16,20,24,28,33,38,43,49,55,62,68,72,85,94,103,112]

    if d1 == 0:
        return 0

    d1 = max(1,int(d1/6))

    for i,v in enumerate(tbl):

        if d1 <= v:
            return i
        
    return len(tbl)-1
    

def parse_scriabin( ifn ):

    ped_off = { 'dtick':0, 'sec':0, 'type':'ped', 'd0':64, 'd1':0 }
    
    noteL = [ ped_off ]
    
    with open(ifn,"r") as f:
        rdr = csv.DictReader(f)

        for r in rdr:
            if r['type'].strip() in [ 'non','nof' ]:
                x = { 'dtick': int(r['dtick']),
                      'sec':   float(r['amicro']) / 1000000.0,
                      'type':  r['type'],
                      'd0':    int(r['D0']),
                      'd1':    invert_velocity(int(r['D1'])) }

                noteL.append(x)

    return noteL
            
    
def insert_scriabin( scoreL, noteL, insert_loc, insert_after_fl ):

    status_map = { 'non':144, 'nof':144, 'ped':176 }
    outL = []

    fieldL = list(scoreL[0].keys())
    offs_sec = 0
    oloc = None
    insert_fl = True
    
    for s in scoreL:
            
        if len(s['loc'])>0 and int(s['loc']) == insert_loc and insert_fl:

            insert_fl = False
            
            print( f"LOC: {insert_loc} oloc:{oloc}" )
            
            if insert_after_fl:
                s['sec'] = float(s['sec']) + offs_sec
                outL.append(s)

            offs_sec = float(s['sec'])
            dur_sec = 0
            for n in noteL:
                d = { f:None  for f in fieldL }
                dur_sec = max(dur_sec,n['sec'])
                d['sec']    = offs_sec + n['sec']
                d['opcode'] = n['type']
                d['status'] = status_map[n['type'].strip()]
                d['d0']     = n['d0']
                d['d1']     = n['d1']
                d['tick']   = n['dtick']
                outL.append(d)
            offs_sec = dur_sec

            if not insert_after_fl:
                s['sec'] = float(s['sec']) + offs_sec
                outL.append(s)
                
        else:
            s['sec'] = float(s['sec']) + offs_sec
            outL.append(s)


        if s['oloc']:
            oloc = s['oloc']
            

    return outL

def write_meta_cfg( o_cfg_fn, name, beg_loc, end_loc ):

    cfg = { "player_name": name,
            "take_label": f"{name}_0_0",
            "session_number": 0,
            "take_number": 0,
            "beg_loc": beg_loc,
            "end_loc": end_loc,
            "skip_score_follow_fl": False }

    with open(o_cfg_fn,"w") as f:
        json.dump(cfg,f)

        

    
def write_output( out_dir, out_fn, outL, beg_loc, end_loc, fieldnamesL ):

    odir = os.path.join(out_dir,out_fn,out_fn)
    os.makedirs( odir, exist_ok=True )

    o_csv_fn = os.path.join(odir,out_fn+".csv")
    o_cfg_fn = os.path.join(odir,"meta.cfg")

    write_meta_cfg(o_cfg_fn,out_fn,beg_loc,end_loc)
    
    with open(o_csv_fn,"w") as f:
        wtr = csv.DictWriter(f,fieldnames=fieldnamesL)

        wtr.writeheader()

        for r in outL:
            wtr.writerow(r)

            

if __name__ == "__main__":
    score_fn = "/home/kevin/src/cwtest/src/cwtest/cfg/gutim_full/data/score/20231028/temp.csv"

    out_fn = "/home/kevin/src/cwtest/src/cwtest/cfg/gutim_full/data/score/20231028/temp_with_scriabin.csv"

    out_dir = "/home/kevin/src/cwtest/src/cwtest/cfg/gutim_full/data"

    fileL = [
        #{ "ifn":"scriabin_etude_op8_3_b_minor.csv",              "insert_loc": 2234, "after_fl":True,  "ofn":"scriabin_8_3",  "beg_loc":775, "end_loc":776 },
        ## { "ifn":"scriabin_etude_op8_2_f_sh_minor.csv",           "insert_loc": 4084, "after_fl":True, "ofn":"scriabin_8_2", "beg_loc":4084, "end_loc":4085 },
        #{ "ifn":"scriabin_etude_op8_2_f_sh_minor.csv",           "insert_loc": 4390, "after_fl":True,  "ofn":"scriabin_8_2",  "beg_loc":1659,  "end_loc":1660  },
        #{  "ifn":"scriabin_etude_op8_9_g_sh_minor.csv",          "insert_loc": 8450, "after_fl":False, "ofn":"scriabin_8_9",  "beg_loc":3832,  "end_loc":3833 },
        #{  "ifn":"scriabin_etude_op65_1_allegro fantastico.csv", "insert_loc":10619, "after_fl":False, "ofn":"scriabin_65_1", "beg_loc":4989, "end_loc":4990 },
        { "ifn":"scriabin_etude_op42_7_f_minor.csv",             "insert_loc":12436, "after_fl":False, "ofn":"scriabin_42_7", "beg_loc":6044, "end_loc":6045 }
        
    ]
    

    scoreL = parse_score(score_fn)
    
    fieldnamesL = list(scoreL[0].keys())


    
    for f in fileL:

        outL   = []

        noteL = parse_scriabin(f['ifn'])

        outL = insert_scriabin(scoreL, noteL, f['insert_loc'], f['after_fl'] )

        write_output( out_dir, f['ofn'], outL, f['beg_loc'], f['end_loc'], fieldnamesL )
        
