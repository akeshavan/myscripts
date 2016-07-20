__author__ = 'kjordan'

import dtitk_wrapper_mod2runsmooth as dw
#from pipe_dti_metrics import dtitk_wf
import nipype.interfaces.dipy as dipype
from nipype.interfaces.fsl import ExtractROI
import os
from glob import glob
from subprocess import check_call
import numpy as np
import nibabel as nib

from nipype.interfaces.fsl import maths
from nipype.interfaces.utility import IdentityInterface
import nipype.pipeline.engine as pe
from nipype.interfaces.fsl.maths import Threshold,MathsCommand, MultiImageMaths, BinaryMaths,ApplyMask

def comparison_wf(subject_id, basedir, sinkdir):

    #create input node
    inputspec = pe.Node(IdentityInterface(fields=['premask', 'prefa', 'pread', 'premd', 'prerd', 'preb0', 'postmask', \
                                                  'postfa', 'postad', 'postmd', 'postrd', 'postb0', 'prexfm', \
                                                  'postxfm', 'commonsp_volume']), name='inputspec')

    #AIM1: move everything to common space
    pre2common_node = pe.Node(name='pre2common_node', interface=dw.dtitkSVResampleTask())
    pre2common_node.inputs.in_arraysz = '128 128 64'
    pre2common_node.inputs.in_voxsz = '2.2 2.2 2'
    pre2common_node.inputs.out_path = '/home/kjordan/testing_preresamp.nii.gz'

    post2common_node = pe.Node(name='post2common_node', interface=dw.dtitkSVResampleTask())
    post2common_node.inputs.in_arraysz = '128 128 64'
    post2common_node.inputs.in_voxsz = '2.2 2.2 2'
    post2common_node.inputs.out_path = '/home/kjordan/testing_postresamp.nii.gz'

    post2pre_node = pe.Node(name='post2pre_node', interface=dw.dtitkdiffeoScalarVolTask())
    post2pre_node.inputs.out_path = '/home/kjordan/testing_postresamp_inpre.nii.gz'

    #AIM2: CREATE A JOINT MASK PRE AND POST SURGERY
    #create mask sum node
    mask_sum_node = pe.Node(name='mask_sum_node', interface=BinaryMaths())
    mask_sum_node.inputs.operation = 'add'

    #create mask thresh_node
    mask_thresh_node = pe.Node(name='mask_thresh_node', interface=Threshold())
    mask_thresh_node.inputs.thresh = 2
    mask_thresh_node.inputs.args = '-bin'

    #create mask application node
    mask_app_node = pe.Node(name='mask_app_node', interface=ApplyMask())

    '''
    #AIM2: REDO METRICS FROM THESE NEW IMAGES
    #create_dti_node
    pre_dti_node = pe.Node(name= 'dti_node', interface=dipype.DTI())
    post_dti_node = pre_dti_node.clone('post_dti_node')

    #create_thresh_node
    pre_thresh_node = pe.Node(name='thresh_node', interface=Threshold())
    pre_thresh_node.inputs.thresh = 0.15
    pre_thresh_node.inputs.args = '-bin'
    post_thresh_node = pre_thresh_node.clone('post_thresh_node')

    #create uthresh node
    pre_uthresh_node = pe.Node(name='uthresh_node', interface=Threshold())
    pre_uthresh_node.inputs.thresh = 0.1
    pre_uthresh_node.inputs.direction = 'above'
    pre_uthresh_node.inputs.args = '-bin'
    post_uthresh_node = pre_uthresh_node.clone('post_uthresh_node')

    #create thresh as percentage node
    pre_threshP_node = pe.Node(name='threshP_node', interface=MathsCommand())
    pre_threshP_node.inputs.args = '-thrP 99'
    post_threshP_node = pre_threshP_node.clone('post_threshP_node')

    #create_binarize_node
    pre_bin_node = pe.Node(name='bin_node', interface=MathsCommand())
    pre_bin_node.inputs.args = '-bin'
    post_bin_node = pre_bin_node.clone('post_bin_node')

    #create b0 extraction node
    pre_b0_node = pe.Node(name='bo_node', interface=ExtractROI())
    pre_b0_node.inputs.t_min=0
    pre_b0_node.inputs.t_size=1
    post_b0_node = pre_b0_node.clone('post_b0_node')
    '''

    '''#create brain extraction node
    bet_node = pe.Node(name='bet_node', interface=BET())
    bet_node.inputs.frac = 0.2
    bet_node.inputs.mask = True

    #create applybet node
    applybet_node = pe.Node(name='applybet_node', interface=ApplyMask())'''

    '''#create scale by 1000 node
    scale1000_node = pe.Node(name='scale1000_node', interface=BinaryMaths())
    scale1000_node.inputs.operation = 'mul'
    scale1000_node.inputs.operand_value = 1000'''
    '''
    #create cluster node
    cluster_node = pe.Node(name='cluster_node', interface=MathsCommand())
    cluster_node.inputs.args = '-tfce 2 0.5 6'
    '''
    #PUT ALL NODES TOGETHER INTO PIPELINE
    import nipype.interfaces.io as nio
    sinker = pe.Node(nio.DataSink(), name="sinker")
    sinker.inputs.base_directory = sinkdir
    sinker.inputs.container = subject_id
    #sinker.inputs.substitutions = []

    pipeline = pe.Workflow(name='pipeline_'+subject_id)
    pipeline.base_dir = basedir

    pipeline.connect(inputspec, 'premask', pre2common_node, 'in_volume')

    pipeline.connect(inputspec, 'postmask', post2common_node, 'in_volume')

    pipeline.connect(post2common_node, 'out_file', post2pre_node, 'in_volume')
    pipeline.connect(inputspec, 'commonsp_volume', post2pre_node, 'in_target')
    pipeline.connect(inputspec, 'postxfm', post2pre_node, 'in_xfm')

    pipeline.connect(pre2common_node, 'out_file', mask_sum_node, 'in_file')
    pipeline.connect(post2pre_node, 'out_file', mask_sum_node, 'operand_file')
    pipeline.connect(mask_sum_node, 'out_file', mask_thresh_node, 'in_file')
    pipeline.connect(mask_thresh_node, 'out_file', sinker, 'joint.mask')


    '''
    pipeline.connect(inputspec, 'pre_ecdata', mask_app_node, 'in_file')
    pipeline.connect(mask_thresh_node, 'out_file', premask_app_node, 'mask_file')
    pipeline.connect(inputspec, 'post_ecdata', postmask_app_node, 'in_file')
    pipeline.connect(mask_thresh_node, 'out_file', postmask_app_node, 'mask_file')
    pipeline.connect(premask_app_node, 'out_file', sinker, 'pre.masked_tensor')
    pipeline.connect(postmask_app_node, 'out_file', sinker, 'post.masked_tensor')

    pipeline.connect(inputspec,'pre_bvec_path', pre_dti_node, 'in_bvec')
    pipeline.connect(inputspec,'pre_bval_path', pre_dti_node, 'in_bval')
    pipeline.connect(inputspec, 'pre_ecdata', pre_dti_node, 'in_file')
    pipeline.connect(inputspec, 'pre_ecdata', b0_node, 'in_file')

    pipeline.connect(pre_dti_node, 'fa_file', pre_thresh_node, 'in_file')
    pipeline.connect(pre_dti_node, 'fa_file', pre_uthresh_node, 'in_file')
    '''

    return pipeline

def finddamage(pt, reg_basepath, pbr_basepath, workingdir, sinkdir, idxfm):

    preop_fa = glob(os.path.join(pbr_basepath, pt+'_pre/dti/*_fa.nii.gz'))[0]
    preop_md = glob(os.path.join(pbr_basepath, pt+'_pre/dti/*_md.nii.gz'))[0]
    preop_rd = glob(os.path.join(pbr_basepath, pt+'_pre/dti/*_rd.nii.gz'))[0]
    preop_ad = glob(os.path.join(pbr_basepath, pt+'_pre/dti/*_ad.nii.gz'))[0]
    preop_b0 = glob(os.path.join(pbr_basepath, pt+'_pre/dti/*_roi.nii.gz'))[0]
    #preop_mask = glob(os.path.join(pbr_basepath, pt+'_pre/dti/*_roi_brain_mask.nii.gz'))[0]
    preop_mask = glob(os.path.join(reg_basepath, pt+'/'+pt+'_postOR/tracking/*_EC_mask.nii.gz'))[0]
    preop_xfm = idxfm
    commonsp_target = glob(os.path.join(reg_basepath, pt+'/'+pt+'_postOR/tracking/*_resamp_aff.nii.gz'))[0]

    postop_fa = glob(os.path.join(pbr_basepath, pt+'_post/dti/*_fa.nii.gz'))[0]
    postop_md = glob(os.path.join(pbr_basepath, pt+'_post/dti/*_md.nii.gz'))[0]
    postop_rd = glob(os.path.join(pbr_basepath, pt+'_post/dti/*_rd.nii.gz'))[0]
    postop_ad = glob(os.path.join(pbr_basepath, pt+'_post/dti/*_ad.nii.gz'))[0]
    postop_b0 = glob(os.path.join(pbr_basepath, pt+'_post/dti/*_roi.nii.gz'))[0]
    #postop_mask = glob(os.path.join(pbr_basepath, pt+'_post/dti/*_roi_brain_mask.nii.gz'))[0]
    postop_mask = glob(os.path.join(reg_basepath, pt+'/'+pt+'_postOR/tracking/*_EC_mask.nii.gz'))[0]
    postop_xfm = glob(os.path.join(reg_basepath, pt+'/'+pt+'_postOR/tracking/*_resamp_aff_diffeo_combo.df.nii.gz'))[0]

    pipl = comparison_wf(pt, workingdir,sinkdir)

    pipl.inputs.inputspec.prefa = preop_fa
    pipl.inputs.inputspec.premd = preop_md
    pipl.inputs.inputspec.prerd = preop_rd
    pipl.inputs.inputspec.pread = preop_ad
    pipl.inputs.inputspec.preb0 = preop_b0
    pipl.inputs.inputspec.premask = preop_mask
    pipl.inputs.inputspec.prexfm = preop_xfm
    pipl.inputs.inputspec.commonsp_volume = commonsp_target

    pipl.inputs.inputspec.postfa = postop_fa
    pipl.inputs.inputspec.postmd = postop_md
    pipl.inputs.inputspec.postrd = postop_rd
    pipl.inputs.inputspec.postad = postop_ad
    pipl.inputs.inputspec.postb0 = postop_b0
    pipl.inputs.inputspec.postmask = postop_mask
    pipl.inputs.inputspec.postxfm = postop_xfm

    pipl.run()


from nipype.utils.filemanip import load_json

debug = True

diff_basepath = '/data/henry8/jordan/prepost/patients/edu_patients'
ptjson = '/home/kjordan/python_code/myscripts/prepost_pipeline/edu_patients.json'

pbr_basepath = '/data/henry8/jordan/prepost/diffpype'
mylist = load_json(ptjson)

step2_basepath = '/data/henry8/jordan/prepost/diffpype_step2'

workingdir = '/scratch/henry_temp/kesshi/wd_prepost_pipe/step2'
identity_xfm = '/home/kjordan/python_code/myscripts/prepost_pipeline/identity.aff'


i=0
UHOH=[]

if debug:
    mylist = mylist[0:1]


for pt in mylist:
    print str(i+1)+'/'+str(len(mylist))
    i+=1
    print pt
    '''
    if not os.path.exists(os.path.join(step2_basepath, pt)):
        os.mkdir(os.path.join(step2_basepath, pt))
    '''

    finddamage(pt, diff_basepath, pbr_basepath, workingdir, step2_basepath, identity_xfm)

    '''try:
        finddamage(pt, diff_basepath)

    except:
        UHOH.append(pt)'''

print "DONE"
print "FAILED"
print UHOH