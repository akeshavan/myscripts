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
reg_node.inputs.output_transform_prefix = 'output_'
reg_node.inputs.transforms = ['Rigid', 'Affine', 'SyN']
reg_node.inputs.transform_parameters = [(0.1,), (0.1,), (0.2, 3.0, 0.0)]
reg_node.inputs.number_of_iterations = [[10000, 11110, 11110]] * 2 + [[100, 30, 20]]
reg_node.inputs.dimension = 3
reg_node.write_composite_transform = True
reg_node.inputs.collapse_output_transforms = True
reg_node.inputs.initial_moving_transform_com = True
#I probably want to do MI??
reg_node.inputs.metric = ['Mattes'] * 2 + [['Mattes', 'CC']]
reg_node.inputs.metric_weight = [1] * 2 + [[0.5, 0.5]]
reg_node.inputs.radius_or_number_of_bins = [32] * 2 + [[32, 4]]
reg_node.inputs.sampling_strategy = ['Regular'] * 2 + [[None, None]]
reg_node.inputs.sampling_percentage = [0.3]*2 + [[None, None]]
reg_node.inputs.convergence_threshold = [1.e-8] * 2 + [-0.01]
reg_node.inputs.convergence_window_size = [20] * 2 + [5]
reg_node.inputs.smoothing_sigmas = [[4, 2, 1]] * 2 + [[1, 0.5, 0]]
reg_node.inputs.sigma_units = ['vox'] * 3
reg_node.inputs.shrink_factors = [[3, 2, 1]]*2 + [[4, 2, 1]]
reg_node.inputs.use_estimate_learning_rate_once = [True]*3
reg_node.inputs.use_histogram_matching = [False]*2+[True]
reg_node.inputs.winsorize_lower_quantile = 0.005
reg_node.inputs.winsorize_upper_quantile = 0.995
reg_node.inputs.args = '--float'
reg_node.inputs.num_threads = 4
#reg_node.inputs.initial_moving_transform = linear_mat
reg_node.inputs.output_warped_image = os.path.abspath('anisotropic_power_map_warped.nii.gz')
#reg_node.inputs.plugin_args = {'sbatch_args': '-c%d' % 4}


pipeline = pe.Workflow(name='pipeline')
pipeline.base_dir = basedir

#pipeline.connect(input_node, 'bvecp', aniso_node, 'bvec_path')
#pipeline.connect(input_node, 'ec_diffdata', aniso_node, 'diffdata')
#pipeline.connect(input_node, 'bmask_diff', aniso_node, 'bmask_path')
pipeline.connect(aniso_node, 'anisopwrmap_savepath', reg_node, 'moving_image')

pipeline.write_graph()

pipeline.run()
