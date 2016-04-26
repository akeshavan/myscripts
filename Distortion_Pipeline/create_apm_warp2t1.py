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

    myshs = sf_to_sh(diffdatashell, gtab_hemisphere, sh_order=6)
    anisomap = anisotropic_power(myshs)
    anisopwr_savepath = os.path.abspath('anisotropic_power_map_sh6.nii.gz')
    img = nib.Nifti1Image(anisomap, aff)
    img.to_filename(anisopwr_savepath)
    return anisopwr_savepath


def nonlinear_reg_diff2t2_workflow(subject_id, subjects_directory, basedir, name='testprocproc'):

    #CREATE NODES
    import nipype.pipeline.engine as pe
    from nipype.interfaces.utility import Function, IdentityInterface
    from nipype.interfaces.ants import Registration

    #create input node
    inputspec = pe.Node(IdentityInterface(fields=['bvec_path', 'diffdata', 'bmaskt1', 'T1', 'fa_path']), name='inputspec')


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
    reg_node.inputs.write_composite_transform = True
    reg_node.inputs.collapse_output_transforms = True
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
    reg_node.inputs.num_threads = 8
    reg_node.inputs.output_warped_image = True

    newreg_node = reg_node.clone(name='newreg_node')

    '''from nipype.interfaces.ants import ApplyTransformsToPoints
    apply2pts = pe.Node(name= 'apply2pts', interface=ApplyTransformsToPoints())'''

    from nipype.interfaces.ants import ApplyTransforms
    apply2ims = pe.Node(name= 'apply2ims', interface=ApplyTransforms())
    apply2ims.inputs.dimension = 3
    apply2ims.inputs.interpolation = 'Linear'

    apply2ims_fa = apply2ims.clone(name='apply2ims_fa')


    #PUT ALL NODES TOGETHER INTO PIPELINE
    import nipype.interfaces.io as nio
    sinker = pe.Node(nio.DataSink(), name="sinker")
    sinker.inputs.base_directory = "/data/henry7/PBR/subjects/"
    sinker.inputs.container = subject_id

    pipeline = pe.Workflow(name=name)
    pipeline.base_dir = basedir

    pipeline.connect(reg_node, "composite_transform", sinker, "dti.nonlinear.@composite")
    pipeline.connect(reg_node, "warped_image", sinker, "dti.nonlinear.@warped")
    pipeline.connect(reg_node, "inverse_composite_transform", sinker, "dti.nonlinear.@invcomp")
    pipeline.connect(reg_node, "inverse_warped_image", sinker, "dti.nonlinear.@invwarp")
    pipeline.connect(aniso_node, "anisopwrmap_savepath", sinker, "dti.nonlinear.@apmap_sh6_diffsp")
    pipeline.connect(apply2ims, "output_image", sinker, "dti.nonlinear.@t1_diffsp")
    pipeline.connect(apply2ims_fa, "output_image", sinker, "dti.nonlinear_fa.@t1_diffsp")

    pipeline.connect(inputspec, 'bvec_path', aniso_node, 'bvec_path')
    pipeline.connect(inputspec, 'diffdata', aniso_node, 'diffdata')
    #pipeline.connect(inputspec, 'bmask_diff', aniso_node, 'bmask_diff')
    pipeline.connect(inputspec, 'T1', reg_node, 'fixed_image')
    pipeline.connect(inputspec, 'bmaskt1', reg_node, 'fixed_image_mask')
    pipeline.connect(aniso_node, 'anisopwrmap_savepath', reg_node, 'moving_image')

    pipeline.connect(aniso_node, 'anisopwrmap_savepath', apply2ims, 'reference_image')
    pipeline.connect(inputspec, 'T1', apply2ims, 'input_image')
    pipeline.connect(reg_node, 'inverse_composite_transform', apply2ims, 'transforms')

    pipeline.connect(inputspec, 'fa_path', apply2ims_fa, 'reference_image')
    pipeline.connect(inputspec, 'T1', apply2ims_fa, 'input_image')
    pipeline.connect(reg_node, 'inverse_composite_transform', apply2ims_fa, 'transforms')

    pipeline.connect(inputspec, 'T1', newreg_node, 'fixed_image')
    pipeline.connect(inputspec, 'bmaskt1', newreg_node, 'fixed_image_mask')
    pipeline.connect(inputspec, 'fa_path', newreg_node, 'moving_image')

    pipeline.connect(newreg_node, "composite_transform", sinker, "dti.nonlinear_fa.@composite")
    pipeline.connect(newreg_node, "warped_image", sinker, "dti.nonlinear_fa.@warped")
    pipeline.connect(newreg_node, "inverse_composite_transform", sinker, "dti.nonlinear_fa.@invcomp")
    pipeline.connect(newreg_node, "inverse_warped_image", sinker, "dti.nonlinear_fa.@invwarp")

    pipeline.write_graph()
    pipeline.config["Execution"] = {"keep_inputs": True, "remove_unnecessary_outputs": False}
    return pipeline
