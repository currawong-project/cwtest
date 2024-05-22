import csv,json,os

def parse_score( score_fn ):

    scoreL = []
    with open(score_fn) as f:
        rdr = csv.DictReader(f)

        for r in rdr:
            d = dict(r)
            d['src']    = "gutim"
            d['loc']    = int(d['loc'])  if d['loc']  else None
            d['oloc']   = int(d['oloc']) if d['oloc'] else None
            d['status'] = int(d['status']) if d['status'] else None
            d['d0']     = int(d['d0']) if d['d0'] else None
            d['d1']     = int(d['d1']) if d['d1'] else None
            d['sec']    = float(d['sec'])
            d['opcode'] = d['opcode'].strip()
            
            scoreL.append(d)
            
            
    return scoreL    


def invert_velocity( d1 ):

    tbl =  [ 1,1,2,2,3,5,8,10,13,16,20,24,28,33,38,43,49,55,62,68,72,85,94,103,112]

    if d1 == 0:
        return 0

    d1 = max(1,int(d1/5))

    for i,v in enumerate(tbl):

        if d1 < v:
            return max(0,i-1)
        
    return len(tbl)-1


def parse_scriabin( ifn ):

    ped_off = { 'dtick':0, 'sec':0, 'type':'ped', 'd0':64, 'd1':0, 'sci_pitch':None, 'UID':None }
    
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
                      'sci_pitch': r['sci_pitch'].strip() if 'sci_pitch' in r else None,
                      'UID':   int(r['UID'])
                     }

                noteL.append(x)

    return noteL
            
    
def insert_scriabin( scoreL, noteL, src_label, insert_loc, insert_after_fl, delta_sec ):

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
                d['sec']       = offs_sec + delta_sec + n['sec']
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


def interleave_scriabin( scoreL, noteL, src_label, beg_score_loc, cut_score_loc, end_scriabin_uid, end_offs_sec ):
    # beg_score_loc: the 'loc' where the inserted scriabin begins
    # cut_score_loc: the 'loc' where the inserted scriabin ends
    # end_scriabin_uid: the 'uid' which syncronizes to the 'cut_score_loc'.
    #
    #          BSL                   CSL 
    # --------------+                 +------------------------------
    #           |   |                 |
    # --------------+                 +------------------------------
    #           |                     |
    #           +-------------------------+
    #           |                     |   |
    #           +-------------------------+
    #                                ESU
    #
    # end_offs_sec is additional offset added to the time of CSL where sync to ESU occurs
    
    def scribian_esu_secs( noteL, end_scriabin_uid ):
        if end_scriabin_uid is None:
            return noteL[-1]['sec']
        
        for d in noteL:
          if d['UID'] == end_scriabin_uid:
              return d['sec']
        assert(0)

    def score_bsl_secs( scoreL, beg_score_loc ):
        for d in scoreL:
            if d['loc'] == beg_score_loc:
                return d['sec']
        assert(0)

    def cut_score_loc_index( scoreL, cut_score_loc ):
        for i,d in enumerate(scoreL):
            if d['loc'] == cut_score_loc:
                return i
        assert(0)

    def assign_event_id( scoreL ):
        # Set a matching 'eid' for each note-on/off
        # and each pedal-dn/up event.  
        

        def _is_note_on(d):
            return d['status'] == 144 and d['d1'] is not None and d['d1']>0
        
        def _is_note_off(d):
            return d['status'] == 144 and d['d1'] is not None and d['d1']==0

        def _is_pedal_dn(d):
            return d['opcode'] == 'ped' and d['d1'] >= 64

        def _is_pedal_up(d):
            return d['opcode'] == 'ped' and d['d1'] < 64

        def _set_end_evt_eid(scoreL,i,d,evt_id,func):
            for n in scoreL[i:]:
                if func(n) and n['d0'] == d['d0']:
                    n['eid'] = evt_id
                    return

            assert(0)
                    
            

        evt_id = 0
        for i,d in enumerate(scoreL):
            if _is_note_on(d):
                _set_end_evt_eid(scoreL,i,d,evt_id,_is_note_off)

            elif _is_pedal_dn(d):
                _set_end_evt_eid(scoreL,i,d,evt_id,_is_pedal_up)

            
            if 'eid' not in d:
                d['eid'] = evt_id;
                evt_id += 1


    def offset_scriabin( noteL, offset_sec ):
        for d in noteL:
            d['sec'] += offset_sec

    def offset_score_after_cut( scoreL, cut_score_loc, secs ):


        # Score index of the first score note to play
        # at the end of the scriabin sequence        
        csl_index = cut_score_loc_index( scoreL, cut_score_loc )
        
        csl_eid = scoreL[csl_index]['eid']
        

        # offset all events that start on or after csl_index
        # (this will not shift note-off's/pedal-ups that
        # are associated with note-on/pedal-dn's which occur
        # before 'csl_index'.

        sec0 = None
        for d in scoreL[csl_index:]:

            if sec0 is not None:
                dsec = d['sec'] - sec0
                secs += dsec

            sec0 = d['sec']
            
            if d['eid'] >= csl_eid:
                d['sec'] = secs


    def scriabin_to_score( scoreL, noteL, src_label ):
        
        status_map = { 'non':144, 'nof':144, 'ped':176, 'ctl':176 }
        type_map   = { 'non':'non', 'nof':'nof', 'ped':'ctl', 'ctl':'ctl' }
        
        for n in noteL:
            d = {}
            d['meas']      = None
            d['loc']       = None
            d['oloc']      = None
            d['sec']       = float(n['sec'])
            d['opcode']    = type_map[ n['type'].strip() ]
            d['status']    = status_map[n['type'].strip()]
            d['d0']        = n['d0']
            d['d1']        = n['d1']
            d['tick']      = n['dtick']
            d['sci_pitch'] = n['sci_pitch']
            d['src']       = src_label
            scoreL.append(d)

        return sorted(scoreL,key=lambda x:x['sec'])


    def score_to_csv_debug(scoreL):

        fieldnames = list(scoreL[0].keys())
        with open("foo.csv","w") as f:
            wtr = csv.DictWriter(f,fieldnames)
            wtr.writeheader()
            for r in scoreL:
                wtr.writerow(r)
                
                
    def remove_eid_field(scoreL):
        for i,d in enumerate(scoreL):
            if 'eid' in d:
                del d['eid']
            scoreL[i] = d
        
        
                    
    # Offset in seconds to be applied to the scriabin to
    # sync it's start with 'beg_score_loc'
    bsl_secs  = score_bsl_secs( scoreL, beg_score_loc )


    # Assign matching note-on/off events the same evt-id
    assign_event_id(scoreL)

    score_to_csv_debug(scoreL)
    
    # Shift scriabin to start at the beg_score_loc
    offset_scriabin(noteL,bsl_secs)

    # Start location in seconds of the second part of the score.
    esu_secs  = scribian_esu_secs( noteL, end_scriabin_uid ) + end_offs_sec

    # Shift the second part of score to begin at 'esu_secs'
    # (while not shifting the end events (note-off/ped-up)
    # for events which started before the cut)

    offset_score_after_cut( scoreL, cut_score_loc, esu_secs )

    scoreL = scriabin_to_score( scoreL, noteL, src_label )

    remove_eid_field( scoreL )

    return scoreL

    
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

        meas0 = None
        f.write("source  meas oloc  op   secs\n")
        f.write("------  ---- ----- ---- ----------\n")
        
        r0 = None
        for r in scoreL:

        
            if r['opcode']=='ped' or r['oloc']:

                src  = r['src']
                meas = r['meas']      if r['meas'] else ""
                oloc = r['oloc']      if r['oloc'] else ""
                label= r['sci_pitch'] if r['opcode']=='non' else _pedal_label(r)
                secs = r['sec']

                if meas:
                    meas0 = meas
                
                s = f"{src:7} {meas:4} {oloc:5} {label:5} {secs}\n"
                f.write(s)

                if r0 and (r0['src'] == 'gutim' and r['src'] != 'gutim'):
                    print(r['src'],'m:',meas0,r['oloc'],end=" ")
                    
                if r0 and (r0['src'] != 'gutim' and r['src'] == 'gutim'):
                    print(r0['oloc'])

                r0 = r

def insert_pedal( scoreL, beg_oloc, end_oloc ):

    def _ped_msg( secs, d1 ):
        return { "opcode":"ctl","loc":None,"oloc":None,"sec":secs,"status":176,"d0":64,"d1":d1,"src":"ped" }

    state = 'dn'
    for d in scoreL:
        if state=='dn' and d['oloc'] == beg_oloc:
            outL.append( _ped_msg( d['sec'], 64 ) )
            state = 'up'
                         
                    
        if state =='up' and d['oloc'] == end_oloc:
            outL.append( _ped_msg( d['sec'], 0 ))
            stae =  None
            break

    return sorted(scoreL, key=lambda x:x['sec'])

        
    

if __name__ == "__main__":
    base_dir = "/home/kevin/src/cwtest/src/cwtest/cfg/gutim_full"
    score_fn = "data/score/20231028/temp.csv"

    ref_fn = "ref_2.txt"
    out_fn = "temp_with_scriabin_2.csv"
    out_dir= "data/score_scriabin/20240428"
    
    in_preset_fn  = "preset_select/m1_458_trans_5.txt"
    out_preset_fn = "preset_select/m1_458_trans_5_scriabin_4.txt"

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
        { "src":"74_3",  "ifn":"scriabin_prelude_op74_3.csv",        "insert_loc": 3718, "after_fl":True,  "ofn":"scriabin_op74_3",  "beg_loc":1275, "end_loc":1276 },
        
        # good
        { "src":"74_2",  "ifn":"scriabin_prelude_op74_2.csv",        "insert_loc": 4088, "after_fl":False,  "ofn":"scriabin_op74_2",  "beg_loc":1383, "end_loc":1384 },

        { "src":"65_1",  "ifn":"scriabin_etude_op65_1_allegro fantastico.csv",  "insert_loc": 4390, "after_fl":True,  "ofn":"scriabin_65_1",  "beg_loc":1659,  "end_loc":1660  },
        

        # good 
        { "src":"74_4",  "ifn":"scriabin_prelude_op74_4.csv",        "insert_loc": 8160, "after_fl":True,  "ofn":"scriabin_op74_4",  "beg_loc":3676, "end_loc":3677 },

        { "src":"8_3",  "ifn":"scriabin_etude_op8_3_b_minor.csv",    "insert_loc": 8450, "after_fl":False,  "ofn":"scriabin_8_3",  "beg_loc":3832,  "end_loc":3883  },
        
        # good
        { "src":"74_5",  "ifn":"scriabin_prelude_op74_5.csv",        "insert_loc": 9567, "after_fl":False,  "ofn":"scriabin_op74_5",  "beg_loc":4470, "end_loc":4471 },

        
        { "src":"65_2",  "ifn":"scriabin_etude_op65_2_allegretto.csv",  "insert_loc": 10789, "after_fl":False,  "ofn":"scriabin_65_2",  "beg_loc":5440,  "end_loc":5441  },

        { "src":"42_7", "ifn":"scriabin_etude_op42_7_f_minor.csv",       "insert_loc":12436, "after_fl":False, "ofn":"scriabin_42_7", "beg_loc":6044, "end_loc":6045 },

        
        { "src":"65_3",  "ifn":"scriabin_etude_op65_3_molta_vivace.csv", "insert_loc": 13848, "after_fl":True,  "ofn":"scriabin_65_3",  "beg_loc":6740,  "end_loc":6741  },
        
        
    ]

    fileL = [

        # *
        { "src":"74_1",  "ifn":"scriabin_prelude_op74_1.csv",        "insert_loc": 1229, "after_fl":False,  "ofn":"scriabin_op74_1",  "beg_loc":417, "end_loc":418, "delta_sec":0.0 },

        # *
        { "src":"74_2",  "ifn":"scriabin_prelude_op74_2.csv",        "insert_loc": 1867, "after_fl":False,  "ofn":"scriabin_op74_2",  "beg_loc":638, "end_loc":639, "delta_sec":0.0 },

        # * 
        { "src":"74_4",  "ifn":"scriabin_prelude_op74_4.csv",        "insert_loc": 2909, "after_fl":True,  "ofn":"scriabin_op74_4",  "beg_loc":1010, "end_loc":1011, "delta_sec":0.0 },
        
        # *
        { "src":"74_3",  "ifn":"scriabin_prelude_op74_3.csv",        "insert_loc": 4084, "after_fl":False,  "ofn":"scriabin_op74_3",  "beg_loc":1383, "end_loc":1384, "delta_sec":0.0 },
        

        
        # 
        #{ "src":"65_1",  "ifn":"scriabin_etude_op65_1_allegro fantastico.csv",  "insert_loc": 6323, "after_fl":True,  "ofn":"scriabin_65_1",  "beg_loc":2763,  "end_loc":2764, "delta_sec":0.0  },
        { "src":"65_1",  "ifn":"scriabin_etude_op65_1_allegro fantastico.csv",  "insert_loc": 6376, "after_fl":False,  "ofn":"scriabin_65_1",  "beg_loc":2804,  "end_loc":2805, "delta_sec":0.0  },

        # * 
        { "src":"8_3",  "ifn":"scriabin_etude_op8_3_b_minor.csv",    "insert_loc": 8450, "after_fl":False,  "ofn":"scriabin_8_3",  "beg_loc":3832,  "end_loc":3883, "delta_sec":0.0  },

        # *
        { "src":"74_5",  "ifn":"scriabin_prelude_op74_5.csv",        "insert_loc": 9567, "after_fl":False,  "ofn":"scriabin_op74_5",  "beg_loc":4470, "end_loc":4471, "delta_sec":0.0 },

        # *
        { "src":"65_2",  "ifn":"scriabin_etude_op65_2_allegretto.csv",  "insert_loc": 10789, "after_fl":False,  "ofn":"scriabin_65_2",  "beg_loc":5440,  "end_loc":5441, "delta_sec":0.0  },

        # *
        { "src":"42_7", "ifn":"scriabin_etude_op42_7_f_minor.csv",       "insert_loc":12428, "after_fl":False, "ofn":"scriabin_42_7", "beg_loc":6043, "end_loc":6044, "delta_sec":0.0 },
        
        #{ "src":"65_3",  "ifn":"scriabin_etude_op65_3_molta_vivace.csv", "insert_loc": 13848, "after_fl":True,  "ofn":"scriabin_65_3",  "beg_loc":6740,  "end_loc":6741, "delta_sec":0.0  },
        { "src":"65_3",  "ifn":"scriabin_etude_op65_3_molta_vivace.csv", "insert_loc": 13953, "after_fl":True,  "ofn":"scriabin_65_3",  "beg_loc":6780,  "end_loc":6781, "delta_sec":0.0  },
        
        
    ]

    # beg_score_loc: score location which syncs w/ scriabin start
    # cut_score_loc: location where score starts again
    # end_scriabin_uid: uid of scriabin which syncs to 'cut_score_loc'.
    fileL = [

        # *
        { "src":"74_1",  "ifn":"scriabin_prelude_op74_1.csv",   "beg_score_loc":1229, "cut_score_loc":1231,  "end_scriabin_uid":743, "end_offs_sec":0, "ofn":"scriabin_op74_1" },

        # *
        { "src":"74_2",  "ifn":"scriabin_prelude_op74_2.csv",   "beg_score_loc": 1867, "cut_score_loc":1877,  "end_scriabin_uid":631,  "end_offs_sec":1.0,  "ofn":"scriabin_op74_2"  },


        # * 
        #{ "src":"74_4",  "ifn":"scriabin_prelude_op74_4.csv",        "insert_loc": 2909, "after_fl":True,  "ofn":"scriabin_op74_4",  "beg_loc":1010, "end_loc":1011, "delta_sec":0.0 },
        #{ "src":"74_4",  "ifn":"scriabin_prelude_op74_4.csv",        "beg_score_loc":2924, "cut_score_loc":2927,  "end_scriabin_uid":917, "end_offs_sec":0, "ofn":"scriabin_op74_4" },
         { "src":"74_4",  "ifn":"scriabin_prelude_op74_4.csv",        "beg_score_loc":2998, "cut_score_loc":3003,  "end_scriabin_uid":917, "end_offs_sec":0, "ofn":"scriabin_op74_4" },
        
        
        # *
        #{ "src":"74_3",  "ifn":"scriabin_prelude_op74_3.csv",        "insert_loc": 4084, "after_fl":False,  "ofn":"scriabin_op74_3",  "beg_loc":1383, "end_loc":1384, "delta_sec":0.0 },
        #{ "src":"74_3",  "ifn":"scriabin_prelude_op74_3.csv",        "beg_score_loc":4062, "cut_score_loc":4070,  "end_scriabin_uid":804, "end_offs_sec":0, "ofn":"scriabin_op74_3" },
        { "src":"74_3",  "ifn":"scriabin_prelude_op74_3.csv",        "beg_score_loc": 4086, "cut_score_loc":4087,  "end_scriabin_uid":804, "end_offs_sec":2.0,  "ofn":"scriabin_op74_3" },
        

        
        # 
        #{ "src":"65_1",  "ifn":"scriabin_etude_op65_1_allegro fantastico.csv",  "insert_loc": 6323, "after_fl":True,  "ofn":"scriabin_65_1",  "beg_loc":2763,  "end_loc":2764, "delta_sec":0.0  },
        { "src":"65_1",  "ifn":"scriabin_etude_op65_1_allegro fantastico.csv",  "insert_loc": 6376, "after_fl":False,  "ofn":"scriabin_65_1",  "beg_loc":2804,  "end_loc":2805, "delta_sec":0.0  },

        # * 
        #{ "src":"8_3",  "ifn":"scriabin_etude_op8_3_b_minor.csv",    "insert_loc": 8450, "after_fl":False,  "ofn":"scriabin_8_3",  "beg_loc":3832,  "end_loc":3883, "delta_sec":0.0  },
        { "src":"8_3",  "ifn":"scriabin_etude_op8_3_b_minor.csv",    "insert_loc": 8446, "after_fl":False,  "ofn":"scriabin_8_3",  "beg_loc":3832,  "end_loc":3883, "delta_sec":0.0  },

        # *
        #{ "src":"74_5",  "ifn":"scriabin_prelude_op74_5.csv",        "insert_loc": 9567, "after_fl":False,  "ofn":"scriabin_op74_5",  "beg_loc":4470, "end_loc":4471, "delta_sec":0.0 },
        { "src":"74_5",  "ifn":"scriabin_prelude_op74_5.csv",        "beg_score_loc": 9566, "cut_score_loc":9574,  "end_scriabin_uid":1168, "end_offs_sec":0.0,  "ofn":"scriabin_op74_5" },

        # *
        #{ "src":"65_2",  "ifn":"scriabin_etude_op65_2_allegretto.csv",  "insert_loc": 10789, "after_fl":False,  "ofn":"scriabin_65_2",  "beg_loc":5440,  "end_loc":5441, "delta_sec":0.0  },
        { "src":"65_2",   "ifn":"scriabin_etude_op65_2_allegretto.csv",   "beg_score_loc": 10790, "cut_score_loc":10789,  "end_scriabin_uid":479, "end_offs_sec":2.0,  "ofn":"scriabin_op65_2" },

        # *
        { "src":"42_7", "ifn":"scriabin_etude_op42_7_f_minor.csv",       "insert_loc":12428, "after_fl":False, "ofn":"scriabin_42_7", "beg_loc":6043, "end_loc":6044, "delta_sec":0.0 },
        
        { "src":"65_3",  "ifn":"scriabin_etude_op65_3_molta_vivace.csv", "insert_loc": 13953, "after_fl":True,  "ofn":"scriabin_65_3",  "beg_loc":6780,  "end_loc":6781, "delta_sec":0.0  },
        
    ]
    
    scoreL = parse_score(score_fn)
    
    fieldnamesL = list(scoreL[0].keys())
    
    for f in fileL:

        print(f" processing; {f['ifn']}")

        noteL = parse_scriabin(f['ifn'])

        if 'beg_score_loc' in f:
            scoreL = interleave_scriabin( scoreL, noteL, f['src'], f['beg_score_loc'],f['cut_score_loc'], f['end_scriabin_uid'], f['end_offs_sec'] )
        else:
            scoreL = insert_scriabin(     scoreL, noteL, f['src'], f['insert_loc'], f['after_fl'], f['delta_sec'] )
        

    if 1:
        assign_loc(scoreL)

        olocMapD = assign_oloc(scoreL)

        max_oloc = max( r['oloc'] for r in scoreL if r['oloc'] )

        print(f"max oloc:{max_oloc}")

        write_output( out_dir, out_fn, scoreL, 0, max_oloc, fieldnamesL )


        remap_preset_locs( in_preset_fn, out_preset_fn, olocMapD )

        gen_reference( scoreL, out_dir, ref_fn )
