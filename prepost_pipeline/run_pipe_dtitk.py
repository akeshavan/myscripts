__author__ = 'kjordan'

from glob import glob
import numpy as np
import os
from pipe_dtitk import dtitk_wf
import nipype.pipeline.engine as pe

debug = True

subject_file = '/home/kjordan/python_code/myscripts/prepost_pipeline/edu_subjects.txt'
workingdir = '/scratch/henry_temp/kesshi/wd_prepost_pipe'
#metaworkflow = pe.Workflow("mwf", base_dir=workingdir)

lines = np.loadtxt(subject_file,dtype='string')
basedir = lines[0]
sublist = lines[1:]
missing_diffdata = []
toomany = []
goodsubs = []

if debug == True:
    sublist = sublist[1:2]

for sub in sublist:
    foundprepost = 0

    ptdir = os.path.join(basedir,sub)
    print "PROCESSING "+ptdir

    ec_diffdata_pre = glob(os.path.join(ptdir,'*preOR/tracking/E*EC.nii.gz'))
    ec_diffdata_post = glob(os.path.join(ptdir,'*postOR/tracking/E*EC.nii.gz'))
    ec_bvec_pre = glob(os.path.join(ptdir,'*preOR/tracking/E*EC.bvec'))
    ec_bval_pre = glob(os.path.join(ptdir,'*preOR/tracking/E*EC.bval'))
    ec_bvec_post = glob(os.path.join(ptdir,'*postOR/tracking/E*EC.bvec'))
    ec_bval_post = glob(os.path.join(ptdir,'*postOR/tracking/E*EC.bval'))

    if len(ec_diffdata_pre)==0 or len(ec_bvec_pre)==0 or len(ec_bval_pre)==0:
        missing_diffdata.append('PRE '+ptdir)
    else:
        if len(ec_diffdata_pre)>1 or len(ec_bvec_pre)>1 or len(ec_bval_pre)>1:
            toomany.append('PRE '+ptdir)
        else:
            foundprepost += 1
        ec_diffdata_pre = ec_diffdata_pre[0]
        ec_bvec_pre = ec_bvec_pre[0]
        ec_bval_pre = ec_bval_pre[0]
    if len(ec_diffdata_post)==0 or len(ec_bvec_post)==0 or len(ec_bval_post)==0:
        missing_diffdata.append('POST '+ptdir)
    else:
        if len(ec_diffdata_post)>1 or len(ec_bvec_post)>1 or len(ec_bval_post)>1:
            toomany.append('POST '+ptdir)
        else:
            foundprepost += 1
        ec_diffdata_post = ec_diffdata_post[0]
        ec_bvec_post = ec_bvec_post[0]
        ec_bval_post = ec_bval_post[0]

    if foundprepost ==2:
        print "FOUND EVERYTHING... proceeding to execute workflow"
        diffwf = dtitk_wf(sub, basedir)
        diffwf.inputs.inputspec.bvec_path = ec_bvec_pre
        diffwf.inputs.inputspec.bval_path = ec_bval_pre
        diffwf.inputs.inputspec.diffdata = ec_diffdata_pre

        diffwf.run()


print "MISSING"
print missing_diffdata
print ">1 Diffusion File"
print toomany