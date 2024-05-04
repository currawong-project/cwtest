import csv,json,os

def parse_score( score_fn ):

    scoreL = []
    with open(score_fn) as f:
        rdr = csv.DictReader(f)

        for r in rdr:
            d = dict(r)
            d['src']  = "gutim"
            d['loc']  = int(d['loc'])  if d['loc']  else None
            d['oloc'] = int(d['oloc']) if d['oloc'] else None
            scoreL.append(d)
            
            
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

    ped_off = { 'dtick':0, 'sec':0, 'type':'ped', 'd0':64, 'd1':0, 'sci_pitch':None }
    
    noteL = []
    
    with open(ifn,"r") as f:
        rdr = csv.DictReader(f)

        for r in rdr:
            type_label = r['type'].strip()
            
            if type_label in [ 'non','nof','ctl','ped' ]:

                if type_label == 'ctl' and int(r['D0'])==64:
                    r['type'] = 'ped'
                
                x = { 'dtick': int(r['dtick']),
                      'sec':   float(r['amicro']) / 1000000.0,
                      'type':  type_label,
                      'd0':    int(r['D0']),
                      'd1':    invert_velocity(int(r['D1'])) if type_label=='non' else int(r['D1']) ,
                      'sci_pitch': r['sci_pitch'].strip() if 'sci_pitch' in r else None
                     }

                noteL.append(x)

    return noteL
            
    
def insert_scriabin( scoreL, noteL, src_label, insert_loc, insert_after_fl ):

    status_map = { 'non':144, 'nof':144, 'ped':176, 'ctl':176 }
    type_map   = { 'non':'non', 'nof':'nof', 'ped':'ctl', 'ctl':'ctl' }
    outL = []

    fieldL    = list(scoreL[0].keys())
    offs_sec  = 0
    oloc      = None
    insert_fl = True
    ped_dn_fl = False
    
    for s in scoreL:

        if s['opcode'] == 'ctl' and s['d0']==64:
            ped_dn_fl = s['d1']!=0
            
            
        if s['loc'] and int(s['loc']) == insert_loc and insert_fl:

            insert_fl = False
            
            print( f"LOC: {insert_loc} oloc:{oloc} ped:{ped_dn_fl}" )
            
            if insert_after_fl:
                s['sec'] = float(s['sec']) + offs_sec
                outL.append(s)

            offs_sec = float(s['sec'])
            dur_sec = 0
            for n in noteL:
                d = { f:None  for f in fieldL }
                dur_sec = max(dur_sec,n['sec'])
                d['sec']       = offs_sec + n['sec']
                d['opcode']    = type_map[ n['type'].strip() ]
                d['status']    = status_map[n['type'].strip()]
                d['d0']        = n['d0']
                d['d1']        = n['d1']
                d['tick']      = n['dtick']
                d['sci_pitch'] = n['sci_pitch']
                d['src']       = src_label
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

    os.makedirs( out_dir, exist_ok=True )

    o_csv_fn = os.path.join(out_dir,out_fn)
    o_cfg_fn = os.path.join(out_dir,"meta.cfg")

    write_meta_cfg(o_cfg_fn,out_fn,beg_loc,end_loc)
    
    with open(o_csv_fn,"w") as f:
        wtr = csv.DictWriter(f,fieldnames=fieldnamesL)

        wtr.writeheader()

        for r in outL:
            wtr.writerow(r)


def assign_loc( scoreL ):

    loc = 0
    for r in scoreL:
        if r['opcode'] == 'non':
            r['loc'] = loc
            loc += 1
        else:
            r['loc'] = None

def assign_oloc( scoreL ):

    olocMapD = {}
    sec0     = None
    oloc     = -1
    
    for r in scoreL:
        
        if r['opcode'] == 'non':

            # if this note-on is not part of a chord with the previous note-on
            if sec0 is None or r['sec'] != sec0:
                sec0 = r['sec']
                oloc += 1  # then advance the oloc counter

            # keep track of the old-oloc -> new-oloc mapping
            olocMapD[ r['oloc'] ] = oloc
            
            r['oloc'] = oloc
            
        else:
            r['oloc'] = None
        
    return olocMapD

def remap_preset_locs( in_fn, out_fn, olocMapD ):

    with open(in_fn) as f:
        fragL = []
        presetD = json.load(f)

        for r in presetD['fragL']:

            r['begPlayLoc'] = olocMapD[ int( r['begPlayLoc'] ) ]
            r['endPlayLoc'] = olocMapD[ int( r['endPlayLoc'] ) ]
            r['endLoc']     = olocMapD[ int( r['endLoc'] ) ]
            
            fragL.append(r)
            

    with open(out_fn,"w") as f:
        presetD['fragL'] = fragL
        presetD['fragN'] = len(fragL)
        json.dump( presetD, f)
        
def gen_reference( scoreL, out_dir, out_fn ):

    def _pedal_label( r ):
        s = ""
        if r['opcode'] in ['ped','ctl']:
            s= 'pup' if int(r['d1']) == 0 else 'pdn' 
        return s
            
    out_fn = os.path.join(out_dir,out_fn)

    with open(out_fn,"w") as f:
        for r in scoreL:
            
            if r['opcode']=='ped' or r['oloc']:

                src  = r['src']
                meas = r['meas'] if r['meas'] else ""
                oloc = r['oloc'] if r['oloc'] else ""
                label= r['sci_pitch'] if r['opcode']=='non' else _pedal_label(r)
                secs = r['sec']
                
                s = f"{src:7} {meas:4} {oloc:5} {label:5} {secs}\n"
                f.write(s)

def insert_pedal( scoreL, locL ):

    def _ped_msg( secs, d1 ):
        return { "opcode":"ctl","loc":None,"oloc":None,"sec":secs,"status":176,"d0":64,"d1":d1,"src":"ped" }
    
    for dn_loc,up_loc in locL:

        assert( dn_loc < up_loc )

        outL = []
        
        for i,r in enumerate(scoreL):
            
            if r['oloc'] == dn_loc:
                outL.append(_ped_msg(r["secs"],64))
                
            if r['oloc'] == up_loc:
                outL.append(_ped_msg(r["secs"],0))


            outL.append(r)

        

            
            
        
    

if __name__ == "__main__":
    base_dir = "/home/kevin/src/cwtest/src/cwtest/cfg/gutim_full"
    score_fn = "data/score/20231028/temp.csv"

    ref_fn = "ref.txt"
    out_fn = "temp_with_scriabin_0.csv"
    out_dir= "data/score_scriabin/20240428"
    
    in_preset_fn  = "preset_select/m1_458_trans_5.txt"
    out_preset_fn = "preset_select/m1_458_trans_5_scriabin.txt"

    score_fn      = os.path.join(base_dir, score_fn)
    out_dir       = os.path.join(base_dir, out_dir)
    in_preset_fn  = os.path.join(base_dir, in_preset_fn)
    out_preset_fn = os.path.join(base_dir, out_preset_fn)
    

    
    fileL = [
        #{ "src":"8_3",  "ifn":"scriabin_etude_op8_3_b_minor.csv",              "insert_loc": 2234, "after_fl":True,  "ofn":"scriabin_8_3",  "beg_loc":775, "end_loc":776 },
        #{ "src":"65_1",  "ifn":"scriabin_etude_op65_1_allegro fantastico.csv",        "insert_loc": 2234, "after_fl":True,  "ofn":"scriabin_65_1",  "beg_loc":775, "end_loc":776 },
        { "src":"65_2",  "ifn":"scriabin_etude_op65_2_allegretto.csv",        "insert_loc": 2234, "after_fl":True,  "ofn":"scriabin_65_2",  "beg_loc":775, "end_loc":776 },
        #{ "src":"65_3",  "ifn":"scriabin_etude_op65_3_molta_vivace.csv",        "insert_loc": 2234, "after_fl":True,  "ofn":"scriabin_65_3",  "beg_loc":775, "end_loc":776 },
        
        #{ "src":"8_2",  "ifn":"scriabin_etude_op8_2_f_sh_minor.csv",           "insert_loc": 4390, "after_fl":True,  "ofn":"scriabin_8_2",  "beg_loc":1659,  "end_loc":1660  },
        #{ "src":"8_3",  "ifn":"scriabin_etude_op8_3_b_minor.csv",               "insert_loc": 4390, "after_fl":True,  "ofn":"scriabin_8_3",  "beg_loc":1659,  "end_loc":1660  },
        { "src":"65_1",  "ifn":"scriabin_etude_op65_1_allegro fantastico.csv",  "insert_loc": 4390, "after_fl":True,  "ofn":"scriabin_65_1",  "beg_loc":1659,  "end_loc":1660  },
        #{ "src":"65_2",  "ifn":"scriabin_etude_op65_2_allegretto.csv",          "insert_loc": 4390, "after_fl":True,  "ofn":"scriabin_65_2",  "beg_loc":1659,  "end_loc":1660  },
        #{ "src":"65_3",  "ifn":"scriabin_etude_op65_3_molta_vivace.csv",        "insert_loc": 4390, "after_fl":True,  "ofn":"scriabin_65_3",  "beg_loc":1659,  "end_loc":1660  },
        
        #{ "src":"8_9",  "ifn":"scriabin_etude_op8_9_g_sh_minor.csv",           "insert_loc": 8450, "after_fl":False, "ofn":"scriabin_8_9",  "beg_loc":3832,  "end_loc":3833 },
        { "src":"8_3",  "ifn":"scriabin_etude_op8_3_b_minor.csv",               "insert_loc": 8450, "after_fl":False,  "ofn":"scriabin_8_3",  "beg_loc":3832,  "end_loc":3883  },
        #{ "src":"65_1",  "ifn":"scriabin_etude_op65_1_allegro fantastico.csv",  "insert_loc": 8450, "after_fl":False,  "ofn":"scriabin_65_1",  "beg_loc":3832,  "end_loc":3883  },
        #{ "src":"65_2",  "ifn":"scriabin_etude_op65_2_allegretto.csv",          "insert_loc": 8450, "after_fl":False,  "ofn":"scriabin_65_2",  "beg_loc":3832,  "end_loc":3883  },
        #{ "src":"65_3",  "ifn":"scriabin_etude_op65_3_molta_vivace.csv",        "insert_loc": 8450, "after_fl":False,  "ofn":"scriabin_65_3",  "beg_loc":3832,  "end_loc":3883  },

        
        #{ "src":"65_1", "ifn":"scriabin_etude_op65_1_allegro fantastico.csv",  "insert_loc":10619, "after_fl":False, "ofn":"scriabin_65_1", "beg_loc":4989, "end_loc":4990 },
        { "src":"65_3",  "ifn":"scriabin_etude_op65_3_molta_vivace.csv",        "insert_loc": 10619, "after_fl":False,  "ofn":"scriabin_65_3",  "beg_loc":4989,  "end_loc":4990  },

        #{ "src":"42_7", "ifn":"scriabin_etude_op42_7_f_minor.csv",             "insert_loc":12436, "after_fl":False, "ofn":"scriabin_42_7", "beg_loc":6044, "end_loc":6045 }
        #{ "src":"49_1", "ifn":"scriabin_etude_op49_1.csv",                     "insert_loc":12436, "after_fl":False, "ofn":"scriabin_49_1", "beg_loc":6044, "end_loc":6045 }
        #{ "src":"56_4", "ifn":"scriabin_etude_op56_4.csv",                      "insert_loc":12436, "after_fl":False, "ofn":"scriabin_56_4", "beg_loc":6044, "end_loc":6045 }
        #{ "src":"65_2",  "ifn":"scriabin_etude_op65_2_allegretto.csv",          "insert_loc": 12436, "after_fl":False,  "ofn":"scriabin_65_2",  "beg_loc":6044,  "end_loc":6045  },
        { "src":"65_3",  "ifn":"scriabin_etude_op65_3_molta_vivace.csv",        "insert_loc": 12436, "after_fl":False,  "ofn":"scriabin_65_3",  "beg_loc":6044,  "end_loc":6045  },
        
    ]
    
    fileL = [

        # good
        { "src":"74_1",  "ifn":"scriabin_prelude_op74_1.csv",        "insert_loc": 2228, "after_fl":True,  "ofn":"scriabin_op74_1",  "beg_loc":774, "end_loc":775 },
        
        # good
        { "src":"74_2",  "ifn":"scriabin_prelude_op74_2.csv",        "insert_loc": 4088, "after_fl":False,  "ofn":"scriabin_op74_2",  "beg_loc":1383, "end_loc":1384 },

        # good
        { "src":"74_3",  "ifn":"scriabin_prelude_op74_3.csv",        "insert_loc": 3718, "after_fl":True,  "ofn":"scriabin_op74_3",  "beg_loc":1275, "end_loc":1276 },

        # good 
        { "src":"74_4",  "ifn":"scriabin_prelude_op74_4.csv",        "insert_loc": 8160, "after_fl":True,  "ofn":"scriabin_op74_4",  "beg_loc":3676, "end_loc":3677 },

        # good
        { "src":"74_5",  "ifn":"scriabin_prelude_op74_5.csv",        "insert_loc": 9567, "after_fl":False,  "ofn":"scriabin_op74_5",  "beg_loc":4470, "end_loc":4471 },

        
        { "src":"65_2",  "ifn":"scriabin_etude_op65_2_allegretto.csv",  "insert_loc": 10789, "after_fl":False,  "ofn":"scriabin_65_2",  "beg_loc":5440,  "end_loc":5441  },

        { "src":"65_3",  "ifn":"scriabin_etude_op65_3_molta_vivace.csv", "insert_loc": 13848, "after_fl":True,  "ofn":"scriabin_65_3",  "beg_loc":6740,  "end_loc":6741  },
        
        
    ]

    scoreL = parse_score(score_fn)
    
    fieldnamesL = list(scoreL[0].keys())
    
    for f in fileL:

        print(f" processing; {f['ifn']}")

        noteL = parse_scriabin(f['ifn'])

        scoreL = insert_scriabin(scoreL, noteL, f['src'], f['insert_loc'], f['after_fl'] )

    
    assign_loc(scoreL)
    
    olocMapD = assign_oloc(scoreL)
    
    max_oloc = max( r['oloc'] for r in scoreL if r['oloc'] )

    print(f"max oloc:{max_oloc}")
    
    write_output( out_dir, out_fn, scoreL, 0, max_oloc, fieldnamesL )
        

    remap_preset_locs( in_preset_fn, out_preset_fn, olocMapD )

    gen_reference( scoreL, out_dir, ref_fn )
