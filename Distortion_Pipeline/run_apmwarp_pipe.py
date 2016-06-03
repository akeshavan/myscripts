import os
from glob import glob
from create_apm_warp2t1 import nonlinear_reg_diff2t2_workflow
from subprocess import call

subfile = '/home/kjordan/python_code/mydata_4myscripts/darpa'
with open(subfile) as f:
    ptlist = f.read().splitlines()

datadir = '/data/henry7/PBR/subjects'
workingdir = '/scratch/henry_temp/kesshi/CHANGLAB/new_working_dir4'
import nipype.pipeline.engine as pe
metaworkflow = pe.Workflow("mwf", base_dir=workingdir)

for pt in ptlist:
    ptdir = os.path.join(datadir, pt)
    ptdiffdir = glob(ptdir+'/dti/ec*')[0]
    ptworkingdir = os.path.join(workingdir, pt)
    print ptdiffdir
    sub_bvec = glob(ptdiffdir+'/*_rotated.bvec')[0]
    print sub_bvec
    sub_ec_diff = glob(ptdiffdir+'/*_corrected.nii.gz')[0]
    print sub_ec_diff
    subT1 = glob(ptdir+'/nii/*MPRAGE.nii.gz')[0]
    print subT1
    subfa = glob(ptdiffdir+'/*_corrected_fa.nii.gz')[0]
    subt1mask = glob(ptdir+'/masks/ec*/brain_mask.nii.gz')[0]
    subdiffmask = glob(ptdiffdir+'/brain_mask_warped_thresh.nii.gz')[0]
    bettedfa = os.path.join(ptdiffdir, 'fa_masked.nii.gz')
    bettedt1 = glob(ptdir+'/masks/ec*/t1_masked.nii.gz')[0]
    call(['fslmaths', subfa, '-mul', subdiffmask, bettedfa])

    nlwf = nonlinear_reg_diff2t2_workflow(pt, datadir, ptworkingdir, name=pt)
    nlwf.inputs.inputspec.bvec_path = sub_bvec
    nlwf.inputs.inputspec.diffdata = sub_ec_diff
    nlwf.inputs.inputspec.T1 = bettedt1
    nlwf.inputs.inputspec.fa_path = bettedfa
    nlwf.inputs.inputspec.bmaskt1 = subt1mask
    metaworkflow.add_nodes([nlwf])
    #nlwf.run(plugin="SGE",plugin_args={"qsub_args":
    #                   "-q ms.q -l arch=lx24-amd64 -l h_stack=32M -l h_vmem=32G -v MKL_NUM_THREADS=8"})

metaworkflow.write_graph()
metaworkflow.run(plugin="SGE",plugin_args={"qsub_args": "-q ms.q -l arch=lx24-amd64 -l h_stack=32M -l h_vmem=29G -v MKL_NUM_THREADS=8"})