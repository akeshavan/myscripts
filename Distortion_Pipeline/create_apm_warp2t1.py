__author__ = 'kjordan'

import os

T1_from_pbr = '/data/henry7/PBR/subjects/kmj0105/nii/ec105-kmj0105-000-MPRAGE.nii.gz'
ecdiff_from_pbr = '/data/henry7/PBR/subjects/kmj0105/dti/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-000/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-000_corrected.nii.gz'
bvec_from_pbr = '/data/henry7/PBR/subjects/kmj0105/dti/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-000/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-002_rotated.bvec'
bval_from_pbr = '/data/henry7/PBR/subjects/kmj0105/nii/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-001.bval'
bmask_diff_from_pbr = '/data/henry7/PBR/subjects/kmj0105/dti/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-000/brain_mask_warped_thresh.nii.gz'
aff_from_pbr = '/data/henry7/PBR/subjects/kmj0105/dti/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-000/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-000_corrected_roi_bbreg_ec105-kmj0105-000-MPRAGE.mat'
basedir_from_pbr = '/data/henry7/PBR/subjects/kmj0105/dti/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-000/'


old_bvals = bval_from_pbr
bvecp = bvec_from_pbr
ec_diffdata = ecdiff_from_pbr
bmask_diff = bmask_diff_from_pbr
bvals = bvecp[:-4]+'bval'
T1 = T1_from_pbr
linear_mat = aff_from_pbr
basedir = basedir_from_pbr

import nipype.pipeline.engine as pe
from nipype.interfaces.utility import Function, IdentityInterface
from nipype.interfaces.ants import Registration


def create_anisopowermap(bvec_path, diffdata, bmask_path):
    import os
    from dipy.reconst.shm import anisotropic_power
    from dipy.reconst.csdeconv import ConstrainedSphericalDeconvModel
    from dipy.io import read_bvec_file
    from dipy.core.gradients import gradient_table_from_bvals_bvecs
    import numpy as np
    import nibabel as nib

    bvecs, bvals = read_bvec_file(bvec_path)
    maskimg = nib.load(bmask_path)
    aff = maskimg.get_affine()
    maskdata = maskimg.get_data()
    mdiffdata = nib.load(diffdata).get_data()

    gtab = gradient_table_from_bvals_bvecs(bvals, np.transpose(bvecs))
    csd_model = ConstrainedSphericalDeconvModel(gtab, None, sh_order=6)
    csd_fit = csd_model.fit(mdiffdata, maskdata)
    anisomap = anisotropic_power(csd_fit.shm_coeff)
    anisopwr_savepath = os.path.abspath('anisotropic_power_map.nii.gz')
    print anisopwr_savepath
    img = nib.Nifti1Image(anisomap, aff)
    img.to_filename(anisopwr_savepath)
    return anisopwr_savepath

#copy bvecs into dti folder so that the names match for dipy function
import shutil
shutil.copyfile(old_bvals,bvals)

#create input node
#input_node = pe.Node(IdentityInterface(fields=['bvecp', 'ec_diffdata', 'bmask_diff']), name='input_node')

#create anisotropic powermap node
aniso_node = pe.Node(name = 'aniso_node', interface=Function(input_names=['bvec_path', 'diffdata', 'bmask_path'],
                                                             output_names=['anisopwrmap_savepath'],
                                                             function=create_anisopowermap))
aniso_node.inputs.bvec_path = bvecp
aniso_node.inputs.diffdata = ec_diffdata
aniso_node.inputs.bmask_path = bmask_diff


#create registration node
reg_node = pe.Node(name= 'reg_node', interface=Registration())
reg_node.inputs.fixed_image = T1
#reg_node.inputs.moving_image = 'anisopwrmap'
reg_node.inputs.output_transform_prefix = 'warptransform_'
reg_node.inputs.initial_moving_transform = linear_mat
reg_node.inputs.transforms = ['SyN']
reg_node.inputs.dimension = 3
reg_node.inputs.metric = ['MI']
reg_node.inputs.write_composite_transform=True
reg_node.inputs.output_warped_image = os.path.abspath('anisotropic_power_map_warped.nii.gz')
reg_node.inputs.smoothing_sigmas = [[1,0],[2,1,0]]
reg_node.inputs.sigma_units = ['vox']*2
reg_node.inputs.shrink_factors = [[2,1],[3,2,1]]
reg_node.inputs.metric_weight = [1]*2

pipeline = pe.Workflow(name='pipeline')
pipeline.base_dir = basedir

#pipeline.connect(input_node, 'bvecp', aniso_node, 'bvec_path')
#pipeline.connect(input_node, 'ec_diffdata', aniso_node, 'diffdata')
#pipeline.connect(input_node, 'bmask_diff', aniso_node, 'bmask_path')
pipeline.connect(aniso_node, 'anisopwrmap_savepath', reg_node, 'moving_image')

pipeline.write_graph()

pipeline.run()