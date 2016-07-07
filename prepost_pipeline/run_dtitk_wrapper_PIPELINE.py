__author__ = 'kjordan'

import dtitk_wrapper_mod2runsmooth as dw
import os
from glob import glob
from subprocess import check_call
import numpy as np
import nibabel as nib

def check_mean(filename):
    data = nib.load(filename).get_data()
    print data.shape
    b0=data[:,:,:,:,0]
    print b0.shape
    mean=np.mean(b0)
    print mean
    return mean


def wmreg(pt, diff_basepath):
    ptpath = os.path.join(diff_basepath, pt)
    prepath = os.path.join(ptpath, pt+'_preOR/tracking')
    postpath = os.path.join(ptpath, pt+'_postOR/tracking')

    # CHECK TO ENSURE TENSORS WERE SAVED... IF NOT, RERUN FIT TENSOR NOTE: this requires old dipy version
    pretensor_list = glob(os.path.join(prepath, '*_EC_tensor.nii.gz'))
    posttensor_list = glob(os.path.join(postpath, '*_EC_tensor.nii.gz'))
    ecdata_pre_path = os.path.join(prepath, '*_EC.nii.gz')
    ecdata_post_path = os.path.join(postpath, '*_EC.nii.gz')

    ecdata_pre = glob(ecdata_pre_path)[0]
    ecdata_post = glob(ecdata_post_path)[0]

    if len(pretensor_list)<1:
        print os.path.join(prepath, '*_EC.nii.gz')
        ecdata_pre = glob(ecdata_pre_path)[0]
        check_call(['fit_tensor', ecdata_pre, '--save_tensor', '--scale=1000'])
    else:
        print "tensor exists...moving on"

    if len(posttensor_list)<1:
        ecdata_post = glob(ecdata_post_path)[0]
        check_call(['fit_tensor', ecdata_post, '--save_tensor', '--scale=1000'])
    else:
        print "tensor exists...moving on"

    pretensor = glob(os.path.join(prepath, '*_EC_tensor.nii.gz'))[0]
    pretensor_resamp = pretensor.replace('.nii.gz', '_resamp.nii.gz')
    posttensor = glob(os.path.join(postpath, '*_EC_tensor.nii.gz'))[0]
    posttensor_resamp = posttensor.replace('.nii.gz', '_resamp.nii.gz')
    posttensor_resamp_aff2pre = posttensor_resamp.replace('.nii.gz', '.aff')

    postbvec = glob(ecdata_post_path.replace('.nii.gz', '.bvec'))[0]

    #check that the scale is correct NOTE: this requires the old version of dipy to run correctly
    premean = check_mean(glob(pretensor)[0])
    postmean = check_mean(glob(posttensor)[0])
    if premean <0.01:
        print "bad scaling of tensor... scaling by 1000"
        bad_tensor.append("pre_"+pt)
        check_call(['fit_tensor', glob(ecdata_pre_path)[0], '--save_tensor', '--scale=1000'])
    if postmean <0.01:
        print "bad scaling of tensor... scaling by 1000"
        bad_tensor.append("post_"+pt)
        check_call(['fit_tensor', glob(ecdata_post_path)[0], '--save_tensor', '--scale=1000'])
    #Create text files to use for inputting moving image
    posttxt = os.path.join(postpath, 'posttensor_txtlist.txt')
    posttxt_aff = posttxt.replace('.txt', '_aff.txt')

    if not os.path.exists(posttxt):
        posttxtfile = open(posttxt, 'w')
        posttxtfile.write(posttensor_resamp)
        posttxtfile.close()

    if not os.path.exists(posttxt_aff):
        posttxtfile_aff = open(posttxt_aff, 'w')
        posttxtfile_aff.write(posttensor_resamp.replace('.nii.gz', '_aff.nii.gz'))
        posttxtfile_aff.close()

    #Resample the pre and postop tensors (for some reason, they interpolate in-plane coming off scanner)
    dres_pre = dw.dtitkResampleTask()
    dres_pre.inputs.in_tensor = pretensor
    dres_pre.inputs.in_arraysz = '128 128 64'
    dres_pre.inputs.in_voxsz = '2.2 2.2 2'
    dres_pre.inputs.out_path = pretensor_resamp

    dres_post = dw.dtitkResampleTask()
    dres_post.inputs.in_tensor = posttensor
    dres_post.inputs.in_arraysz = '128 128 64'
    dres_post.inputs.in_voxsz = '2.2 2.2 2'
    dres_post.inputs.out_path = posttensor_resamp

    #Create a trace image and use it to make a brain mask
    dtool_tr = dw.dtitkTVtoolTask()
    dtool_tr.inputs.in_tensor = pretensor_resamp
    dtool_tr.inputs.in_flag = 'tr'

    bt = dw.dtitkBinThreshTask()
    bt.inputs.in_image = pretensor_resamp.replace('.nii.gz', '_tr.nii.gz')
    bt.inputs.out_path = pretensor_resamp.replace('.nii.gz', '_trbmask.nii.gz')
    bt.inputs.in_numbers = '0.01 100 1 0'

    #Apply rigid transformation
    drr = dw.dtitkRigidTask()
    drr.inputs.in_fixed_tensor = pretensor_resamp
    drr.inputs.in_moving_txt = posttxt
    drr.inputs.in_similarity_metric = 'EDS'

    #Apply affine transformation
    dar = dw.dtitkAffineTask()
    dar.inputs.in_fixed_tensor = pretensor_resamp
    dar.inputs.in_moving_txt = posttxt
    dar.inputs.in_similarity_metric = 'EDS'
    dar.inputs.in_usetrans_flag = '--useTrans'

    #Apply diffeomorphic transformation
    ddr = dw.dtitkDiffeoTask()
    ddr.inputs.in_fixed_tensor = pretensor_resamp
    ddr.inputs.in_moving_txt = posttxt_aff
    ddr.inputs.in_mask = pretensor_resamp.replace('.nii.gz', '_trbmask.nii.gz')
    ddr.inputs.in_numbers = '6 0.002'

    #combine affine and diffeomorphic transforms
    dxfm = dw.dtitkComposeXfmTask()
    dxfm.inputs.in_df = posttensor_resamp.replace('.nii.gz', '_aff_diffeo.df.nii.gz')
    dxfm.inputs.in_aff = posttensor_resamp_aff2pre
    dxfm.inputs.out_path = posttensor_resamp.replace('.nii.gz', '_aff_diffeo_combo.df.nii.gz')

    #apply combo transform
    daxfm = dw.dtitkSymTensor3DVolTask()
    daxfm.inputs.in_tensor = posttensor_resamp
    daxfm.inputs.in_xfm = posttensor_resamp.replace('.nii.gz', '_aff_diffeo_combo.df.nii.gz')
    daxfm.inputs.in_target = pretensor_resamp
    daxfm.inputs.out_path = posttensor_resamp.replace('.nii.gz', '_aff_diffeo_combo.nii.gz')

    #make a trace image of the affine and diffeo registered tensor for QC
    dtool_tr_postaff = dw.dtitkTVtoolTask()
    dtool_tr_postaff.inputs.in_tensor = posttensor_resamp.replace('.nii.gz', '_aff.nii.gz')
    dtool_tr_postaff.inputs.in_flag = 'tr'

    dtool_tr_postdiff = dw.dtitkTVtoolTask()
    dtool_tr_postdiff.inputs.in_tensor = posttensor_resamp.replace('.nii.gz', '_aff_diffeo.nii.gz')
    dtool_tr_postdiff.inputs.in_flag = 'tr'

    dtool_tr_postreg = dw.dtitkTVtoolTask()
    dtool_tr_postreg.inputs.in_tensor = posttensor_resamp.replace('.nii.gz', '_aff_diffeo_combo.nii.gz')
    dtool_tr_postreg.inputs.in_flag = 'tr'

    #make a postop brainmask using the trace image
    bt_post = dw.dtitkBinThreshTask()
    bt_post.inputs.in_image = posttensor_resamp.replace('.nii.gz', '_aff_diffeo_combo_tr.nii.gz')
    bt_post.inputs.out_path = posttensor_resamp.replace('.nii.gz', '_aff_diffeo_combo_trbmask.nii.gz')
    bt_post.inputs.in_numbers = '0.01 100 1 0'

    #rotate the postop bvecs to preop NOTE: HAVING TROUBLE WITH ABSOLUTE PATHS
    rotbvec = dw.dtitkRotBvecTask()
    rotbvec.inputs.in_affxfm = posttensor_resamp_aff2pre.split('/')[-1]
    rotbvec.inputs.in_bvecs = postbvec.split('/')[-1]
    print "YEEEE"
    print posttensor_resamp_aff2pre
    print postbvec
    print "sss"

    #move the postop EC data to the preop space using diffeo transform NOTE: NOT WORKING... DOENS'T LIKE DIFFDATA
    move_postdata = dw.dtitkScalarVolTask()
    move_postdata.inputs.in_volume = ecdata_pre
    move_postdata.inputs.in_xfm = posttensor_resamp.replace('.nii.gz', '_aff_diffeo_combo.df.nii.gz')
    move_postdata.inputs.in_target = pretensor_resamp
    move_postdata.inputs.out_path = ecdata_post.replace('.nii.gz', '_preresamp_space.nii.gz')

    force_rerun = True
    if not len(glob(os.path.join(postpath, '*_EC_tensor_resamp_aff_diffeo_combo_tr.nii.gz')))>0 or force_rerun:
        print os.path.join(postpath, '*_EC_tensor_resamp_aff_diffeo_combo_tr.nii.gz')
        print pt+" UHOH"
        '''dres_pre.run()
        dres_post.run()
        dtool_tr.run()
        bt.run()
        drr.run()
        dar.run()
        dtool_tr_postaff.run()
        ddr.run()'''
        '''dtool_tr_postdiff.run()'''
        dxfm.run() #note: the pipeline chokes if you don't comment out from here on, run it, then uncomment
        '''daxfm.run()
        dtool_tr_postreg.run()
        bt_post.run()'''
        move_postdata.run()
        owd = os.getcwd()
        os.chdir(postpath)
        rotbvec.run()
        os.chdir(owd)
        print "SUCCESSFULLY EXECUTED"
    else:
        print pt + ' WAS SUCCESSFUL PREVIOUSLY'


from nipype.utils.filemanip import load_json

diff_basepath = '/data/henry8/jordan/prepost/patients/edu_patients'
ptjson = '/home/kjordan/python_code/myscripts/prepost_pipeline/edu_patients.json'
mylist = load_json(ptjson)


i=0
UHOH=[]
bad_tensor = []
for pt in mylist[0:2]:
    print str(i)+'/'+str(len(mylist))
    i+=1
    print pt

    wmreg(pt, diff_basepath)
    '''try:
        wmreg(pt, diff_basepath)

    except:
        UHOH.append(pt)'''

print "DONE"
print "FAILED"
print UHOH

print "BAD TENSORS"
print bad_tensor
