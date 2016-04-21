__author__ = 'kjordan'

import os

os.chdir('/data/henry7/PBR/subjects/kmj0105/dti/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-000')

T1_from_pbr = '/data/henry7/PBR/subjects/kmj0105/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-000/nii/ec105-kmj0105-000-MPRAGE.nii.gz'
ecdiff_from_pbr = '/data/henry7/PBR/subjects/kmj0105/dti/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-000/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-000_corrected.nii.gz'
bvec_from_pbr = '/data/henry7/PBR/subjects/kmj0105/dti/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-000/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-002_rotated.bvec'
bval_from_pbr = '/data/henry7/PBR/subjects/kmj0105/nii/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-001.bval'
bmask_diff_from_pbr = '/data/henry7/PBR/subjects/kmj0105/dti/brain_mask_warped_thresh.nii.gz'
aff_from_pbr = '/data/henry7/PBR/subjects/kmj0105/dti/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-000_corrected_roi_bbreg_ec105-kmj0105-000-MPRAGE.mat'

old_bvals = bval_from_pbr
bvecs = bvec_from_pbr
ec_diffdata = ecdiff_from_pbr
bmask_diff = bmask_diff_from_pbr
bvals = bvecs[:-4]+'bval'
T1 = T1_from_pbr
linear_mat = aff_from_pbr

import nipype.pipeline.engine as pe
from nipype.interfaces.utility import Function
from nipype.interfaces.ants import Registration


def create_anisopowermap(bvec_path, diffdata_path, bmask_path):
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
    diffdata = nib.load(diffdata_path).get_data()

    gtab = gradient_table_from_bvals_bvecs(bvals, np.transpose(bvecs))
    csd_model = ConstrainedSphericalDeconvModel(gtab, None, sh_order=6)
    csd_fit = csd_model.fit(diffdata, maskdata)
    anisomap = anisotropic_power(csd_fit.shm_coeff)
    anisopwr_savepath = os.path.abspath('anisotropic_power_map.nii.gz')
    img = nib.Nifti1Image(anisomap, aff)
    img.to_filename(anisopwr_savepath)
    return anisopwr_savepath

#copy bvecs into dti folder so that the names match for dipy function
import shutil
shutil.copyfile(old_bvals,bvals)

#create anisotropic powermap node
aniso_node = pe.Node(name = 'aniso_node', interface=Function(input_names=[bvecs, ec_diffdata, bmask_diff], output_names=[anisopwr_savepath], function=create_anisopowermap))

#create registration node
reg_node = Registration()
reg.inputs.fixed_image = T1
reg.inputs.moving_image = anisopwr_savepath
reg.inputs.output_transform_prefix = 'warptransform_'
reg.inputs.initial_moving_transform = linear_mat
reg.inputs.transforms = ['SyN']
reg.inputs.dimension = 3
reg.inputs.metric = ['MI']
reg.inputs.write_composite_input=True
reg.inputs.output_warped_image = os.path.abspath('anisotropic_power_map_warped.nii.gz')

pipeline = pe.Workflow(name='ants_nonlinear_t1_to_apmap')
pipeline.connect(aniso_node, anisopwr_savepath, reg_node, anisopwr_savepath)

pipeline.run()