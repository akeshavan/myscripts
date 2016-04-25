import os
from glob import glob
from create_apm_warp2t1 import nonlinear_reg_diff2t2_workflow

ptlist = ['kmj0081', 'kmj0082', 'kmj0084', 'kmj0087', 'kmj0091', 'kmj0092', 'kmj0096', 'kmj0099', 'kmj0105', 'kmj0118']
#ptlist = ['kmj0081', 'kmj0082', 'kmj0084', 'kmj0087']
#ptlist = ['kmj0091', 'kmj0092','kmj0105']
#ptlist = ['kmj0096']
#, 'kmj0099', 'kmj0108', 'kmj0118'] #trying on grid (0105 locally)

datadir = '/data/henry7/PBR/subjects'
workingdir = '/scratch/henry_temp/kesshi/CHANGLAB/new_working_dir'
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

    nlwf = nonlinear_reg_diff2t2_workflow(pt, datadir, ptworkingdir, name=pt)
    nlwf.inputs.inputspec.bvec_path = sub_bvec
    nlwf.inputs.inputspec.diffdata = sub_ec_diff
    nlwf.inputs.inputspec.T1 = subT1
    metaworkflow.add_nodes([nlwf])
    #nlwf.run(plugin="SGE",plugin_args={"qsub_args":
    #                   "-q ms.q -l arch=lx24-amd64 -l h_stack=32M -l h_vmem=32G -v MKL_NUM_THREADS=8"})

metaworkflow.write_graph()
metaworkflow.run(plugin="SGE",plugin_args={"qsub_args": "-q ms.q -l arch=lx24-amd64 -l h_stack=32M -l h_vmem=29G -v MKL_NUM_THREADS=8"})