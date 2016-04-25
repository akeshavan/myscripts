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
    from nipype.interfaces import fsl

    #create input node
    inputspec = pe.Node(IdentityInterface(fields=['bvec_path', 'diffdata', 'bmaskt1', 'T1', 'affmat', 'bmaskdiff']), name='inputspec')


    #create anisotropic power map node
    aniso_node = pe.Node(name = 'aniso_node', interface=Function(input_names=['bvec_path', 'diffdata'],
                                                             output_names=['anisopwrmap_savepath'],
                                                             function=create_anisopowermap))
    #create registration node
    reg_node = pe.Node(name= 'reg_node', interface=fsl.FNIRT())
    reg_node.inputs.output_type = 'NIFTI_GZ'

    outputspec = pe.Node(IdentityInterface(fields=['field_file', 'jacobian_file', 'warped_file', 'fieldcoeff_file']), name='outputspec')

    pipeline = pe.Workflow(name='pipeline')
    pipeline.base_dir = basedir

    pipeline.connect(inputspec, 'bvec_path', aniso_node, 'bvec_path')
    pipeline.connect(inputspec, 'diffdata', aniso_node, 'diffdata')

    pipeline.connect(inputspec, 'affmat', reg_node, 'affine_file')
    pipeline.connect(inputspec, 'T1', reg_node, 'ref_file')
    pipeline.connect(inputspec, 'bmaskt1', reg_node, 'refmask_file')
    pipeline.connect(inputspec, 'bmaskdiff', reg_node, 'inmask_file')
    pipeline.connect(aniso_node, 'anisopwrmap_savepath', reg_node, 'in_file')

    #REG NODE TO OUTPUTSPEC
    pipeline.connect(reg_node, 'field_file', outputspec, 'field_file')
    pipeline.connect(reg_node, 'jacobian_file', outputspec, 'jacobian_file')
    pipeline.connect(reg_node, 'warped_file', outputspec, 'warped_file')
    pipeline.connect(reg_node, 'fieldcoeff_file', outputspec, 'fieldcoeff_file')

    pipeline.write_graph()
    return pipeline
