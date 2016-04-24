__author__ = 'kjordan'

def create_anisopowermap(bvec_path, diffdata):
    import os
    import nibabel as nib
    from dipy.reconst.shm import anisotropic_power
    import numpy as np
    from dipy.core.sphere import HemiSphere
    from dipy.reconst.shm import sf_to_sh

    bvecs_xyz = np.loadtxt(bvec_path)
    bvecs_xyz_array = np.array(bvecs_xyz[:,1:]).transpose()
    gtab_hemisphere = HemiSphere(xyz=bvecs_xyz_array)

    img = nib.load(diffdata)
    diffdata = img.get_data()
    diffdatashell = diffdata[:,:,:,1:]
    aff = img.get_affine()

    myshs = sf_to_sh(diffdatashell, gtab_hemisphere, sh_order=2)
    anisomap = anisotropic_power(myshs)
    #Add in a brain masking step here, if beneficial to end result
    anisopwr_savepath = os.path.abspath('anisotropic_power_map.nii.gz')
    img = nib.Nifti1Image(anisomap, aff)
    img.to_filename(anisopwr_savepath)
    return anisopwr_savepath


def nonlinear_reg_diff2t2_workflow(subject_id, subjects_directory, basedir, name='testprocproc'):
    import nipype.pipeline.engine as pe
    from nipype.interfaces.utility import Function, IdentityInterface
    from nipype.interfaces.ants import Registration

    #create input node
    inputspec = pe.Node(IdentityInterface(fields=['bvec_path', 'diffdata', 'bmask_diff', 'T1']), name='inputspec')


    #create anisotropic power map node
    aniso_node = pe.Node(name = 'aniso_node', interface=Function(input_names=['bvec_path', 'diffdata'],
                                                             output_names=['anisopwrmap_savepath'],
                                                             function=create_anisopowermap))
    #create registration node
    reg_node = pe.Node(name= 'reg_node', interface=Registration())
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

    '''outputspec = pe.Node(IdentityInterface(fields=['composite_transform', 'forward_invert_flags', 'forward_transforms',
                                                   'inverse_composite_transform', 'inverse_warped_image',
                                                   'reverse_invert_flags', 'reverse_transforms', 'save_state',
                                                   'warped_image']), name='outputspec')'''

    outputspec = pe.Node(IdentityInterface(fields=['composite_transform','inverse_composite_transform', 'inverse_warped_image','warped_image']), name='outputspec')

    pipeline = pe.Workflow(name='pipeline')
    pipeline.base_dir = basedir

    pipeline.connect(inputspec, 'bvec_path', aniso_node, 'bvec_path')
    pipeline.connect(inputspec, 'diffdata', aniso_node, 'diffdata')
    #pipeline.connect(inputspec, 'bmask_diff', aniso_node, 'bmask_diff')
    pipeline.connect(inputspec, 'T1', reg_node, 'fixed_image')
    #pipeline.connect(inputspec, 'bmaskt1', reg_node, 'fixed_image_mask')
    pipeline.connect(aniso_node, 'anisopwrmap_savepath', reg_node, 'moving_image')
    pipeline.connect(reg_node, 'composite_transform', outputspec, 'composite_transform')
    #pipeline.connect(reg_node, 'forward_invert_flags', outputspec, 'forward_input_flags')
    #pipeline.connect(reg_node, 'forward_tranforms', outputspec, 'forward_tranforms')
    pipeline.connect(reg_node, 'inverse_composite_transform', outputspec, 'inverse_composite_tranform')
    pipeline.connect(reg_node, 'inverse_warped_image', outputspec, 'inverse_warped_image')
    #pipeline.connect(reg_node, 'reverse_invert_flags', outputspec, 'reverse_invert_flags')
    #pipeline.connect(reg_node, 'reverse_transforms', outputspec, 'reverse_transforms')
    #pipeline.connect(reg_node, 'save_state', outputspec, 'save_state')
    pipeline.connect(reg_node, 'warped_image', outputspec, 'warped_image')

    pipeline.write_graph()
    return pipeline

T1_from_pbr = '/data/henry7/PBR/subjects/kmj0105/nii/ec105-kmj0105-000-MPRAGE.nii.gz'
ec_diff_from_pbr = '/data/henry7/PBR/subjects/kmj0105/dti/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-000/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-000_corrected.nii.gz'
bvec_from_pbr = '/data/henry7/PBR/subjects/kmj0105/dti/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-000/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-002_rotated.bvec'
#bmask_diff_from_pbr = '/data/henry7/PBR/subjects/kmj0105/dti/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-000/brain_mask_warped_thresh.nii.gz'
basedir_from_pbr = '/data/henry7/PBR/subjects/kmj0105/dti/ec105-kmj0105-001-ep2d_diff_mddw_64_p2_new-000/'
#bmask_t1_from_pbr = '/data/henry7/PBR/subjects/kmj0105/masks/ec105-kmj0105-000-MPRAGE/brain_mask.nii.gz'

ptlist = ['kmj0081']
subjects_directory = '/data/henry7/PBR/subjects/'

for ptid in ptlist:

    nlwf = nonlinear_reg_diff2t2_workflow(ptid, subjects_directory, basedir_from_pbr)
    nlwf.inputs.inputspec.bvec_path = bvec_from_pbr
    nlwf.inputs.inputspec.diffdata = ec_diff_from_pbr
    #nlwf.inputs.inputspec.inputs.bmaskdiff_path = bmask_diff_from_pbr
    nlwf.inputs.inputspec.T1 = T1_from_pbr
    #nlwf.inputs.inputspec.inputs.bmaskt1 = bmask_t1_from_pbr
    nlwf.run()
    '''nlwf.run(plugin="SGE",plugin_args={"qsub_args":
                       "-q ms.q -l arch=lx24-amd64 -l h_stack=32M -l h_vmem=4G -v MKL_NUM_THREADS=1"})'''
